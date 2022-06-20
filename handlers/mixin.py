#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\

from typing import ClassVar, Iterable, List
from redis import Redis
from queue import Queue

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from http import HTTPStatus

from forms import CreateMixinForm, RestrictMxForm

from storage.channel import Channel
from storage.key import Key
from storage.mixin import Mixin
from storage.user import User

from . import make_abort, ApiRoutes, RequestMethods, AbortResponse
from handlers.channel import confirm_channel, get_base_json_channel
from .errors import MixinError, GrantError, BadKeyError, \
    SelfMixinError, KeyPermissionsError, ChannelError, \
    ChannelNotExistError, BadThreadError, BadKeyTypeError, \
    AlreadyMixedError, CircleMixinError

REDIS_MIXIN_KEY = 'limq_mixin_{channel_id}'


class ChannelIdQueue(Queue):
    def __init__(self):
        super().__init__()

    def put_several(self, items: Iterable):
        for item in items:
            self.put(item)


def confirm_key_on_mixin(key: Key, channel: Channel) -> \
        MixinError or GrantError:
    if key is None or not key.active():
        return BadKeyError()

    if key.chan_id == channel.id:
        return SelfMixinError()

    if not key.can_read():
        return KeyPermissionsError()

    return


StatusCode = int


def confirm_channels(channel_1: Channel, channel_2: Channel, user: User,
                     ) -> (ChannelError or None, StatusCode):
    error = confirm_channel(channel_1, user)
    if error:
        return error, HTTPStatus.FORBIDDEN

    if channel_2 is None:
        return ChannelNotExistError(), HTTPStatus.BAD_REQUEST

    return None, 200


def confirm_restrict_mixin_form(form: RestrictMxForm) -> \
        MixinError or None:
    if not form.channel or not form.subject:
        return BadThreadError()

    if form.mixin_type.data not in ("in", "out"):
        return BadKeyTypeError()

    return


def check_circle_mixin(session, source_id: str, dest_id: str) -> bool:
    def get_dest_ids(mixins: Iterable[Mixin]) -> List[str]:
        return [mixin.dest_channel for mixin in mixins]

    mixins_out_dest = session.query(Mixin).filter(
        Mixin.source_channel == dest_id).all()

    if not mixins_out_dest:
        return True
    queue = ChannelIdQueue()
    queue.put_several(get_dest_ids(mixins_out_dest))

    while not queue.empty():
        next_id = queue.get()
        if next_id == source_id:
            return False

        mixins_out = session.query(Mixin).filter(
            Mixin.source_channel == next_id).all()

        if mixins_out:
            queue.put_several(get_dest_ids(mixins_out))
    return True


def create_handler(sess_cr: ClassVar, rds_sess: Redis) -> Blueprint:
    app = Blueprint("mixin", __name__)

    @app.route(ApiRoutes.GetMixins, methods=[RequestMethods.GET])
    @login_required
    def do_get_mixins():
        channel_id = request.args.get('channel_id', '')
        if not channel_id:
            make_abort(AbortResponse(
                ok=False,
                code=ChannelNotExistError.code,
                description=ChannelNotExistError.description
            ),
                HTTPStatus.UNPROCESSABLE_ENTITY)

        session = sess_cr()

        channel = session.query(Channel). \
            filter(Channel.id == channel_id).first()

        error = confirm_channel(channel, current_user)
        if error:
            return make_abort(AbortResponse(
                ok=False,
                code=error.code,
                description=error.description
            ), HTTPStatus.FORBIDDEN)

        mixin_out = (session.query(Channel).filter(
            Channel.id == mixin.dest_channel).first() for mixin in
                     session.query(Mixin).filter(
                         Mixin.source_channel == channel.id).all())

        mixin_in = (session.query(Channel).filter(
            Channel.id == mixin.source_channel).first() for mixin in
                    session.query(Mixin).filter(
                        Mixin.dest_channel == channel.id).all())

        mixin_out_json = [
            get_base_json_channel(channel) for channel in mixin_out]

        mixin_in_json = [
            get_base_json_channel(channel) for channel in mixin_in
        ]

        return jsonify({'in': mixin_in_json, 'out': mixin_out_json})

    @app.route(ApiRoutes.CreateMixin, methods=[RequestMethods.POST])
    @login_required
    def do_create_mixin():
        """ Handler for mixin creating. """

        form = CreateMixinForm()
        channel = form.channel.data or ''
        mix_key = form.key.data or ''

        session = sess_cr()

        channel = session.query(Channel).filter(
            Channel.id == channel).first()

        error = confirm_channel(channel, current_user)
        if error:
            return make_abort(AbortResponse(
                ok=False,
                code=error.code,
                description=error.description
            ), HTTPStatus.FORBIDDEN)

        key = session.query(Key).filter(Key.key == mix_key).first()
        error = confirm_key_on_mixin(key, channel)

        if error:
            return make_abort(AbortResponse(
                ok=False,
                code=error.code,
                description=error.description
            ), HTTPStatus.FORBIDDEN)

        src_channel = session.query(Channel).filter(
            Channel.id == key.chan_id).first()

        mixin = session.query(Mixin).filter(
            (Mixin.source_channel == src_channel.id) & (
                    Mixin.dest_channel == channel.id)).first()
        if mixin:
            return make_abort(AbortResponse(
                ok=False,
                code=AlreadyMixedError.code,
                description=AlreadyMixedError.description
            ),
                HTTPStatus.BAD_REQUEST)

        if not check_circle_mixin(session, src_channel.id, channel.id):
            return make_abort(AbortResponse(
                ok=False,
                code=CircleMixinError.code,
                description=CircleMixinError.description
            ),
                HTTPStatus.BAD_REQUEST)

        new_mixin = Mixin(source_channel=src_channel.id,
                          dest_channel=channel.id,
                          linked_by=key.key)

        session.add(new_mixin)
        session.commit()

        mixins = rds_sess.get(
            REDIS_MIXIN_KEY.format(channel_id=src_channel.id)) or ''
        if not mixins:
            mixins = new_mixin.dest_channel
        else:
            mixins = mixins.split(',')
            mixins.append(new_mixin.dest_channel)
            mixins = ','.join(mixins)
        rds_sess.set(
            REDIS_MIXIN_KEY.format(channel_id=src_channel.id), mixins)

        return {"mixin": get_base_json_channel(src_channel)}

    @app.route(ApiRoutes.RestrictMixin, methods=[RequestMethods.POST])
    @login_required
    def restrict_out_mx():
        """ Handler for restriction of  mixin. """

        form = RestrictMxForm()

        error = confirm_restrict_mixin_form(form)
        if error:
            return make_abort(AbortResponse(
                ok=False,
                code=error.code,
                description=error.description
            ),
                HTTPStatus.UNPROCESSABLE_ENTITY)

        subject = form.subject.data
        channel_id = form.channel.data

        session = sess_cr()

        channel_1 = session.query(Channel) \
            .filter(Channel.id == subject).first()

        channel_2 = session.query(Channel) \
            .filter(Channel.id == channel_id).first()

        error, code = \
            confirm_channels(channel_1, channel_2, current_user)
        if error:
            return make_abort(AbortResponse(
                ok=False,
                code=error.code,
                description=error.description
            ), code)

        if form.mixin_type.data == "out":
            source_channel_id = channel_1.id
            dest_channel_id = channel_2.id
        else:
            source_channel_id = channel_2.id
            dest_channel_id = channel_1.id

        mixin = session.query(Mixin).filter(
            (Mixin.source_channel == source_channel_id) & (
                    Mixin.dest_channel == dest_channel_id)).first()

        if not mixin:
            return make_abort(AbortResponse(
                ok=False,
                code=BadThreadError.code,
                description=BadThreadError.description
            ),
                HTTPStatus.BAD_REQUEST)

        session.delete(mixin)
        session.commit()

        mixins = rds_sess.get(
            REDIS_MIXIN_KEY.format(channel_id=source_channel_id)) or ''
        if mixins:
            mixins = mixins.split(',')
            mixins.remove(dest_channel_id)
            mixins = ','.join(mixins)
        rds_sess.set(
            REDIS_MIXIN_KEY.format(channel_id=source_channel_id),
            mixins)

        return {'mixin': channel_2.id}

    return app
