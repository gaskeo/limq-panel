#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\

from typing import ClassVar, TypedDict, NamedTuple, Iterable

from flask import Blueprint, jsonify
from flask_login import current_user, login_required
from http import HTTPStatus

from forms import RegisterChannelForm, RenameChannelForm

from storage.channel import Channel
from storage.key import Key
from storage.keygen import generate_channel_id
from storage.user import User

from . import make_abort, ApiRoutes, RequestMethods, AbortResponse
from .errors import ChannelError, ChannelNotExistError, \
    NotChannelOwnerError, ChannelNameError

MAX_CHANNEL_NAME_LENGTH = 64


class KeysTypesCount(TypedDict):
    active: int
    inactive: int


class KeysCount(NamedTuple):
    can_read: KeysTypesCount
    can_write: KeysTypesCount


class ChannelJson(TypedDict):
    channel_id: str
    channel_name: str
    read_keys: KeysTypesCount
    write_keys: KeysTypesCount


class CreateChannelTuple(NamedTuple):
    channel_name: str


class RenameChannelTuple(NamedTuple):
    channel_id: str
    channel_name: str


def get_keys_count(keys: Iterable[Key]) -> KeysCount:
    can_write = can_read = write_active = read_active = 0
    for key in keys:
        if key.can_write():
            can_write += 1
            write_active += key.active()
        if key.can_read():
            can_read += 1
            read_active += key.active()

    return KeysCount(
        can_read=KeysTypesCount(active=read_active,
                                inactive=can_read - read_active),
        can_write=KeysTypesCount(active=write_active,
                                 inactive=can_write - write_active))


def get_base_json_channel(channel: Channel) -> ChannelJson:
    return ChannelJson(channel_id=channel.id,
                       channel_name=channel.name,
                       read_keys=KeysTypesCount(active=0, inactive=0),
                       write_keys=KeysTypesCount(active=0, inactive=0))


def get_json_channel(channel: Channel, session: ClassVar) -> \
        ChannelJson:
    json_channel = get_base_json_channel(channel)

    keys = session.query(Key).filter(
        Key.chan_id == channel.id).all()

    keys_stats = get_keys_count(keys)
    json_channel['read_keys'] = keys_stats.can_read
    json_channel['write_keys'] = keys_stats.can_write
    return json_channel


def get_valid_channel_name(channel_name: str or None) -> str:
    if not channel_name:
        return ''
    channel_name = channel_name.strip()
    if len(channel_name) > MAX_CHANNEL_NAME_LENGTH or \
            not len(channel_name):
        return ''
    return channel_name


def confirm_channel(channel: Channel or None,
                    user: User) -> ChannelError or None:
    if not channel:
        return ChannelNotExistError()

    if channel.owner_id != user.id:
        return NotChannelOwnerError()

    return


def confirm_create_channel_form(
        form: RegisterChannelForm) -> (
        CreateChannelTuple, ChannelError or None):
    valid_channel_name = get_valid_channel_name(form.name.data)
    if not valid_channel_name:
        return CreateChannelTuple(''), ChannelNameError()

    return CreateChannelTuple(valid_channel_name), None


def confirm_edit_channel_form(
        form: RenameChannelForm) -> (
        RenameChannelTuple, ChannelError or None):
    valid_channel_name = get_valid_channel_name(form.name.data)
    if not valid_channel_name:
        return RenameChannelTuple('', ''), ChannelNameError()

    return RenameChannelTuple(form.id.data,
                              valid_channel_name), None


def create_handler(sess_cr: ClassVar) -> Blueprint:
    """
    A closure for instantiating the handler
    that maintains channel processes.
    Must borrow a SqlAlchemy session creator for further usage.

    """

    app = Blueprint("channel", __name__)

    @app.route(ApiRoutes.CreateChannel, methods=[RequestMethods.POST])
    @login_required
    def do_create_channel():
        form = RegisterChannelForm()

        channel_name, error = confirm_create_channel_form(form)
        if error:
            return make_abort(
                AbortResponse(ok=False,
                              code=error.code,
                              description=error.description),
                HTTPStatus.UNPROCESSABLE_ENTITY)

        session = sess_cr()
        channel = Channel(
            name=channel_name,
            id=generate_channel_id(),
            owner_id=current_user.id
        )

        session.add(channel)
        session.commit()
        return jsonify(get_base_json_channel(channel))

    @app.route(ApiRoutes.GetChannels, methods=[RequestMethods.GET])
    @login_required
    def do_get_channel():
        session = sess_cr()
        channels = session.query(Channel) \
            .filter(Channel.owner_id == current_user.id).all()
        if not channels:
            return jsonify([])

        json_channels = [get_json_channel(channel, session)
                         for channel in channels]

        return jsonify(json_channels)

    @app.route(ApiRoutes.RenameChannel, methods=[RequestMethods.PUT])
    @login_required
    def do_edit_channel():
        """ Handler for settings changing page. """

        form = RenameChannelForm()
        (channel_id, channel_name), error = \
            confirm_edit_channel_form(form)
        if error:
            return make_abort(
                AbortResponse(ok=False,
                              code=error.code,
                              description=error.description),
                HTTPStatus.UNPROCESSABLE_ENTITY)

        session = sess_cr()

        # Channel validation.
        channel = session.query(Channel). \
            filter(Channel.id == channel_id).first()

        error = confirm_channel(channel, current_user)
        if error:
            return make_abort(AbortResponse(
                ok=False,
                code=error.code,
                description=error.description
            ), HTTPStatus.FORBIDDEN)

        channel.name = channel_name
        session.commit()

        return jsonify(get_json_channel(channel, sess_cr()))

    return app
