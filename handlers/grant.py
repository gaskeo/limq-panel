#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\

from datetime import datetime
from enum import Enum
from typing import ClassVar, TypedDict, NamedTuple, Literal

from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from http import HTTPStatus

from forms import CreateKeyForm, ToggleKeyActiveForm, DeleteKeyForm

from storage.channel import Channel
from storage.key import Key
from storage.keygen import generate_key

from . import make_abort
from handlers.channel import ChannelMessage, confirm_channel

MAX_KEY_NAME_LENGTH = 50


class KeyMessage(Enum):
    Ok = ""
    KeyError = "Invalid key"
    MixinError = "Mixin with same channel"
    WrongPermissionError = "Wrong permission"


class FormMessage(Enum):
    Ok = ""
    NameError = "Bad key name"
    LongNameError = "Key name too long"
    PermissionsError = "Wrong permissions"


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


def confirm_form(form: CreateKeyForm) -> FormMessage:
    if not form.name.data:
        return FormMessage.NameError.value
    if len(form.name.data) > MAX_KEY_NAME_LENGTH:
        return FormMessage.LongNameError.value

    if form.permissions.data not in "01":
        return FormMessage.PermissionsError.value

    return FormMessage.Ok.value


def get_permission_from_form(
        perm: Literal['0'] or Literal['1']) -> KeyPermission:
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


def create_perm(info: bool, read: bool, write: bool):
    return info << 2 | write << 1 | read


def create_handler(sess_cr: ClassVar) -> Blueprint:
    """
    A closure for instantiating the handler
    that maintains keys processes.
    Must borrow a SqlAlchemy session creator for further usage.
    """

    app = Blueprint("grant", __name__)

    @app.route("/do/grant", methods=["POST"])
    @login_required
    def do_grant():
        form = CreateKeyForm(request.form)

        error_message = confirm_form(form)
        if error_message != FormMessage.Ok.value:
            return make_abort(error_message,
                              HTTPStatus.UNPROCESSABLE_ENTITY)

        session = sess_cr()

        channel_id = form.id.data

        channel: Channel = session.query(Channel). \
            filter(Channel.id == channel_id).first()

        error_message = confirm_channel(channel, current_user)
        if error_message != ChannelMessage.Ok:
            return make_abort(error_message, HTTPStatus.FORBIDDEN)

        key_id = generate_key()
        key = Key(key=key_id, chan_id=channel_id,
                  name=form.name.data, created=datetime.now())

        perm = get_permission_from_form(form.permissions.data)
        info = form.info_allowed.data
        key.perm = create_perm(info, perm.can_read, perm.can_write)

        session.add(key)
        session.commit()

        return jsonify(get_json_key(key))

    @app.route("/do/get_keys", methods=["GET"])
    @login_required
    def do_get_keys():
        channel_id = request.args.get('channel_id', '')
        if not channel_id:
            return make_abort(ChannelMessage.ChannelNotExistError,
                              HTTPStatus.UNPROCESSABLE_ENTITY)

        session = sess_cr()

        channel: Channel = session.query(Channel). \
            filter(Channel.id == channel_id).first()

        error_message = confirm_channel(channel, current_user)
        if error_message != ChannelMessage.Ok.value:
            return make_abort(error_message, HTTPStatus.FORBIDDEN)

        keys = session.query(Key). \
            filter(Key.chan_id == channel_id).all()
        keys_json = [get_json_key(key) for key in keys]

        return jsonify(keys_json)

    @app.route("/do/toggle_key_active", methods=["POST"])
    @login_required
    def do_toggle_key():
        form = ToggleKeyActiveForm(request.form)

        session = sess_cr()

        key = session.query(Key) \
            .filter(Key.key == form.key.data).first()

        if not key:
            return make_abort(KeyMessage.KeyError,
                              HTTPStatus.UNPROCESSABLE_ENTITY)

        channel = session.query(Channel). \
            filter(Channel.id == key.chan_id).first()

        error_message = confirm_channel(channel, current_user)
        if error_message != ChannelMessage.Ok.value:
            return make_abort(error_message, HTTPStatus.FORBIDDEN)

        key.toggle_active()

        session.commit()
        return jsonify(get_json_key(key))

    @app.route("/do/delete_key", methods=["POST"])
    @login_required
    def delete_key():
        """ Handler for deletion of keys """
        form = DeleteKeyForm()
        key_id = form.key.data

        session = sess_cr()

        key: Key = session.query(Key).filter(Key.key == key_id).first()

        if key is None:
            return make_abort(KeyMessage.KeyError,
                              HTTPStatus.UNPROCESSABLE_ENTITY)

        channel: Channel = session.query(Channel). \
            filter(Channel.id == key.chan_id).first()

        error_message = confirm_channel(channel, current_user)
        if error_message != ChannelMessage.Ok.value:
            return make_abort(error_message, HTTPStatus.FORBIDDEN)

        session.delete(key)
        session.commit()
        return {'key': key.key}

    return app
