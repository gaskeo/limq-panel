#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\

from datetime import datetime
from typing import ClassVar, TypedDict, NamedTuple, Literal, Callable

from flask import Blueprint, request, jsonify
from flask_limiter.extension import LimitDecorator
from flask_login import current_user, login_required
from http import HTTPStatus

from redis import Redis

from content_limits import LimitTypes, Limits
from forms import CreateKeyForm, ToggleKeyActiveForm, DeleteKeyForm

from storage.channel import Channel
from storage.key import Key
from storage.keygen import generate_key
from storage.mixin import Mixin
from redis_storage import set_key_permissions, \
    set_key_channel_id
import redis_storage

from . import make_abort, ApiRoutes, RequestMethods, AbortResponse
from handlers.channel import confirm_channel
from .errors import GrantError, BadChannelIdError, BadKeyError, \
    ChannelNotExistError

MAX_KEY_NAME_LENGTH = 20


class KeyJson(TypedDict):
    key: str
    name: str
    channel: str
    read: int
    write: int
    created: str
    active: bool
    info: bool


class KeyPermission(NamedTuple):
    can_read: bool
    can_write: bool


class CreateKeyTuple(NamedTuple):
    channel_id: str
    name: str
    perm: int


def get_valid_key_name(key_name: str or None) -> str:
    key_name = key_name.strip() if key_name else ''
    if len(key_name) > MAX_KEY_NAME_LENGTH or not len(key_name):
        return ''
    return key_name


def get_permission_from_form(
        perm: Literal['0'] or Literal['1']) -> KeyPermission:
    if perm not in "01":
        return KeyPermission(can_read=True, can_write=False)
    read = perm == "0"
    write = read ^ 1
    return KeyPermission(can_read=read, can_write=bool(write))


def get_json_key(key: Key) -> KeyJson:
    return KeyJson(key=key.key,
                   name=key.name,
                   read=key.can_read(),
                   write=key.can_write(),
                   created=str(key.created.date()),
                   active=key.active(),
                   info=key.info_allowed(),
                   channel=key.chan_id)


def create_perm(info: bool, read: bool, write: bool,
                disallow_mixins: bool):
    return disallow_mixins << 3 | info << 2 | write << 1 | read


def confirm_create_key_form(form: CreateKeyForm
                            ) -> (CreateKeyTuple, GrantError):
    valid_channel_id = form.id.data or ''
    if not valid_channel_id:
        return CreateKeyTuple('', '', 0), \
               BadChannelIdError()
    valid_key_name = get_valid_key_name(form.name.data)
    if not valid_key_name:
        return CreateKeyTuple('', '', 0), \
               BadKeyError()

    perm = get_permission_from_form(form.permissions.data)
    info = form.info_allowed.data or False
    disallow_mixins = form.disallow_mixins.data or False
    valid_perm = create_perm(info, perm.can_read, perm.can_write,
                             disallow_mixins)

    return CreateKeyTuple(
        channel_id=valid_channel_id,
        name=valid_key_name,
        perm=valid_perm
    ), None


def create_handler(sess_cr: ClassVar, rds_sess: Redis,
                   limits: Callable[[int, LimitTypes], LimitDecorator]
                   ) -> Blueprint:
    """
    A closure for instantiating the handler
    that maintains keys processes.
    Must borrow a SqlAlchemy session creator for further usage.
    """

    app = Blueprint("grant", __name__)

    @app.route(ApiRoutes.Grant, methods=[RequestMethods.POST])
    @limits(Limits.KeyCreate, LimitTypes.ip)
    @limits(Limits.KeyCreate, LimitTypes.user)
    @login_required
    def do_grant():
        form = CreateKeyForm(request.form)

        (channel_id, name, perm), error = \
            confirm_create_key_form(form)

        if error:
            return make_abort(
                AbortResponse(ok=False,
                              code=error.code,
                              description=error.description),
                HTTPStatus.UNPROCESSABLE_ENTITY)

        session = sess_cr()

        channel = session.query(Channel). \
            filter(Channel.id == channel_id).first()

        error = confirm_channel(channel, current_user)
        if error:
            return make_abort(
                AbortResponse(ok=False,
                              code=error.code,
                              description=error.description),
                HTTPStatus.FORBIDDEN)

        key_id = generate_key()
        key = Key(key=key_id, chan_id=channel_id,
                  name=name, created=datetime.now(),
                  perm=perm)

        session.add(key)
        session.commit()

        set_key_permissions(rds_sess, key.key, perm)
        set_key_channel_id(rds_sess, key.key, channel_id)

        return jsonify(get_json_key(key))

    @app.route(ApiRoutes.GetKeys, methods=[RequestMethods.GET])
    @limits(Limits.GetKeys, LimitTypes.ip)
    @limits(Limits.GetKeys, LimitTypes.user)
    @login_required
    def do_get_keys():
        channel_id = request.args.get('channel_id', '')

        if not channel_id:
            return make_abort(
                AbortResponse(
                    ok=False,
                    code=ChannelNotExistError.code,
                    description=ChannelNotExistError.description),
                HTTPStatus.UNPROCESSABLE_ENTITY)

        session = sess_cr()

        channel: Channel = session.query(Channel). \
            filter(Channel.id == channel_id).first()

        error = confirm_channel(channel, current_user)
        if error:
            return make_abort(AbortResponse(
                ok=False,
                code=error.code,
                description=error.description
            ), HTTPStatus.FORBIDDEN)

        keys = session.query(Key). \
            filter(Key.chan_id == channel_id).all()
        keys_json = [get_json_key(key) for key in keys]

        return jsonify(keys_json)

    @app.route(ApiRoutes.ToggleKey, methods=[RequestMethods.PUT])
    @limits(Limits.KeyToggle, LimitTypes.ip)
    @limits(Limits.KeyToggle, LimitTypes.user)
    @login_required
    def do_toggle_key():
        form = ToggleKeyActiveForm(request.form)
        key_id = form.key.data

        session = sess_cr()

        key = session.query(Key) \
            .filter(Key.key == key_id).first()

        if not key:
            return make_abort(AbortResponse(
                ok=False,
                code=BadKeyError.code,
                description=BadKeyError.description
            ),
                HTTPStatus.UNPROCESSABLE_ENTITY)

        channel = session.query(Channel). \
            filter(Channel.id == key.chan_id).first()

        error = confirm_channel(channel, current_user)
        if error:
            return make_abort(AbortResponse(
                ok=False,
                code=error.code,
                description=error.description
            ), HTTPStatus.FORBIDDEN)

        key.toggle_active()
        session.commit()

        set_key_permissions(rds_sess, key.key, key.perm)
        return jsonify(get_json_key(key))

    @app.route(ApiRoutes.DeleteKey, methods=[RequestMethods.POST])
    @limits(Limits.KeyDelete, LimitTypes.ip)
    @limits(Limits.KeyDelete, LimitTypes.user)
    @login_required
    def delete_key():
        """ Handler for deletion of keys """
        form = DeleteKeyForm()
        key_id = form.key.data

        session = sess_cr()

        key = session.query(Key).filter(Key.key == key_id).first()

        if key is None:
            return make_abort(AbortResponse(
                ok=False,
                code=BadKeyError.code,
                description=BadKeyError.description
            ),
                HTTPStatus.UNPROCESSABLE_ENTITY)

        channel = session.query(Channel). \
            filter(Channel.id == key.chan_id).first()

        error = confirm_channel(channel, current_user)
        if error:
            return make_abort(AbortResponse(
                ok=False,
                code=error.code,
                description=error.description
            ), HTTPStatus.FORBIDDEN)

        session.query(Mixin).filter(
            Mixin.linked_by == key.key).delete()

        session.delete(key)
        session.commit()

        redis_storage.delete_key(rds_sess, key.key)

        return {'key': key.key}

    return app
