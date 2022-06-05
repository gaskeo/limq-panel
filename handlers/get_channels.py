#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


from typing import ClassVar, NamedTuple, Iterable, TypedDict

from flask import Blueprint, jsonify
from flask_login import current_user, login_required

from storage.channel import Channel
from storage.key import Key


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


def get_keys_count(keys: Iterable[Key]) -> KeysCount:
    can_write = can_read = write_active = read_active = 0
    for key in keys:
        if key.can_write():
            can_write += 1
            if key.active():
                write_active += 1
        if key.can_read():
            can_read += 1
            if key.active():
                read_active += 1

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


def create_handler(sess_cr: ClassVar) -> Blueprint:
    """
    A closure for instantiating the handler that maintains channel creating processes.
    Must borrow a SqlAlchemy session creator for further usage.
    :param sess_cr: sqlalchemy.orm.sessionmaker object
    :return Blueprint object
    """

    app = Blueprint("get_channels", __name__)

    @app.route("/do/get_channels", methods=["GET"])
    @login_required
    def do_create_channel():
        session = sess_cr()
        channels = session.query(Channel) \
            .filter(Channel.owner_id == current_user.id).all()
        if not channels:
            return jsonify([])

        json_channels = []

        for channel in channels:
            json_channel = get_json_channel(channel, session)

            json_channels.append(json_channel)
        return jsonify(json_channels)

    return app
