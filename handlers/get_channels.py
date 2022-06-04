#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


from typing import ClassVar, NamedTuple, Iterable, Dict, TypedDict

from flask import Blueprint, redirect, jsonify
from flask_login import current_user, login_required

from storage.channel import Channel
from storage.key import Key


class KeysCount(NamedTuple):
    can_read: int
    can_write: int


class ChannelDict(TypedDict):
    channel_id: str
    channel_name: str
    read_keys: int
    write_keys: int


def get_keys_count(keys: Iterable[Key]) -> KeysCount:
    can_write = can_read = 0
    for key in keys:
        if key.can_write():
            can_write += 1
        if key.can_read():
            can_read += 1
    return KeysCount(can_read=can_read, can_write=can_write)


def get_base_json_channel(channel: Channel) -> ChannelDict:
    return ChannelDict(channel_id=channel.id,
                       channel_name=channel.name,
                       read_keys=0, write_keys=0)


def create_handler(sess_cr: ClassVar) -> Blueprint:
    """
    A closure for instantiating the handler that maintains channel creating processes.
    Must borrow a SqlAlchemy session creator for further usage.
    :param sess_cr: sqlalchemy.orm.sessionmaker object
    :return Blueprint object
    """

    app = Blueprint("get_channels", __name__)

    @app.route("/do/get_channels", methods=["POST"])
    @login_required
    def do_create_channel():
        session = sess_cr()
        channels = session.query(Channel)\
            .filter(Channel.owner_id == current_user.id).all()
        if not channels:
            return []

        json_channels = []

        for channel in channels:
            json_channel = get_base_json_channel(channel)

            keys = session.query(Key).filter(
                Key.chan_id == channel.id).all()

            keys_stats = get_keys_count(keys)
            json_channel['read_keys'] = keys_stats.can_read
            json_channel['write_keys'] = keys_stats.can_write

            json_channels.append(json_channel)
        return jsonify(json_channels)

    return app
