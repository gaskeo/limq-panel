#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\

from enum import Enum
from typing import ClassVar, TypedDict, NamedTuple, Iterable

from flask import Blueprint, jsonify
from flask_login import current_user, login_required
from http import HTTPStatus

from forms import RegisterChannelForm, RenameChannelForm

from storage.channel import Channel
from storage.key import Key
from storage.keygen import channel_identifier
from storage.user import User

from . import make_abort

MAX_CHANNEL_NAME_LENGTH = 50


class FormMessage(Enum):
    Ok = ""
    NameError = "Bad channel name"
    LongNameError = "Channel name too long"


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


class ChannelMessage(Enum):
    Ok = ""
    ChannelNotExistError = "Channel doesn't exist"
    NotOwnerError = "No access to this channel"


def confirm_channel_form(
        form: RegisterChannelForm or RenameChannelForm) -> FormMessage:
    if not form.name.data:
        return FormMessage.NameError.value

    if len(form.name.data) > MAX_CHANNEL_NAME_LENGTH:
        return FormMessage.LongNameError.value

    return FormMessage.Ok.value


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


def confirm_channel(channel: Channel or None,
                    user: User) -> ChannelMessage:
    if not channel:
        return ChannelMessage.ChannelNotExistError.value

    if channel.owner_id != user.id:
        return ChannelMessage.NotOwnerError.value

    return ChannelMessage.Ok.value


def create_handler(sess_cr: ClassVar) -> Blueprint:
    """
    A closure for instantiating the handler
    that maintains channel processes.
    Must borrow a SqlAlchemy session creator for further usage.

    """

    app = Blueprint("channel", __name__)

    @app.route("/do/create_channel", methods=["POST"])
    @login_required
    def do_create_channel():
        form = RegisterChannelForm()

        error_message = confirm_channel_form(form)
        if error_message != FormMessage.Ok.value:
            return make_abort(error_message,
                              HTTPStatus.UNPROCESSABLE_ENTITY)

        session = sess_cr()
        channel = Channel(
            name=form.name.data,
            id=channel_identifier(),
            owner_id=current_user.id
        )

        session.add(channel)
        session.commit()
        return jsonify(get_base_json_channel(channel))

    @app.route("/do/get_channels", methods=["GET"])
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

    @app.route("/do/edit_channel", methods=["POST"])
    @login_required
    def do_edit_channel():
        """ Handler for settings changing page. """

        form = RenameChannelForm()
        error_message = confirm_channel_form(form)
        if error_message != FormMessage.Ok.value:
            return make_abort(error_message,
                              HTTPStatus.UNPROCESSABLE_ENTITY)

        channel_id = form.id.data
        session = sess_cr()

        # Channel validation.
        channel = session.query(Channel). \
            filter(Channel.id == channel_id).first()

        error_message = confirm_channel(channel, current_user)
        if error_message != ChannelMessage.Ok.value:
            return make_abort(error_message, HTTPStatus.FORBIDDEN)

        channel.name = form.name.data
        session.commit()

        return jsonify(get_json_channel(channel, sess_cr()))

    return app
