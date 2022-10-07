#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\

from typing import ClassVar, TypedDict, NamedTuple, Iterable, Callable

from flask import Blueprint, jsonify
from flask_login import current_user, login_required
from http import HTTPStatus
from flask_limiter.extension import LimitDecorator

from forms import RegisterChannelForm, RenameChannelForm
from content_limits import LimitTypes, Limits

from storage.channel import Channel
from storage.key import Key
from storage.keygen import generate_channel_id
from storage.user import User
from storage.user_type import UserType

from . import make_abort, ApiRoutes, RequestMethods, AbortResponse
from .errors import ChannelError, ChannelNotExistError, \
    NotChannelOwnerError, ChannelNameError, ChannelLimitOver, \
    ChannelMaxMessageSizeLimitOver, ChannelBufferLimitOver, \
    ChannelBufferedMessageCountLimitOver, ChannelBufferedDataTTLOver, \
    ChannelEndToEndNotAvailable

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

    max_message_size: int
    need_bufferization: bool
    buffered_message_count: int
    buffered_data_persistency: int
    end_to_end_data_encryption: bool


class CreateChannelTuple(NamedTuple):
    channel_name: str
    max_message_size: int
    need_bufferization: bool
    buffered_message_count: int
    buffered_data_persistency: int
    end_to_end_data_encryption: bool


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
                       write_keys=KeysTypesCount(active=0, inactive=0),
                       max_message_size=0,
                       need_bufferization=False,
                       buffered_message_count=0,
                       buffered_data_persistency=0,
                       end_to_end_data_encryption=False
                       )


def get_json_channel(channel: Channel, session: ClassVar) -> \
        ChannelJson:
    json_channel = get_base_json_channel(channel)

    keys = session.query(Key).filter(
        Key.chan_id == channel.id).all()

    keys_stats = get_keys_count(keys)
    json_channel['read_keys'] = keys_stats.can_read
    json_channel['write_keys'] = keys_stats.can_write

    json_channel['max_message_size'] = channel.max_message_size
    json_channel['need_bufferization'] = channel.need_bufferization
    json_channel['buffered_message_count'] = \
        channel.buffered_message_count
    json_channel['buffered_data_persistency'] = \
        channel.buffered_data_persistency
    json_channel['end_to_end_data_encryption'] = \
        channel.end_to_end_data_encryption
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
        form: RegisterChannelForm, quota: UserType) -> (
        CreateChannelTuple, ChannelError or None):
    valid_channel_name = get_valid_channel_name(form.name.data)
    if not valid_channel_name:
        return (CreateChannelTuple('', 0, False, 0, 0, False),
                ChannelNameError())

    valid_message_size = form.max_message_size.data
    if valid_message_size is None or \
            (valid_message_size > quota.max_message_size or
             valid_message_size < 1):
        return (CreateChannelTuple('', 0, False, 0, 0, False),
                ChannelMaxMessageSizeLimitOver())

    if (valid_need_bufferization := form.need_bufferization.data) and \
            not quota.bufferization:
        return (CreateChannelTuple('', 0, False, 0, 0, False),
                ChannelBufferLimitOver())

    valid_buffered_message_count = valid_buffered_data_persistency = 0
    if valid_need_bufferization:
        valid_buffered_message_count = \
            form.buffered_message_count.data
        if valid_buffered_message_count is None or \
                (valid_buffered_message_count >
                 quota.max_bufferred_message_count or
                 valid_buffered_message_count < 0):
            return (CreateChannelTuple('', 0, False, 0, 0, False),
                    ChannelBufferedMessageCountLimitOver())

        valid_buffered_data_persistency = (
            form.buffered_data_persistency.data)
        if valid_buffered_data_persistency is None or \
                (valid_buffered_data_persistency >
                 quota.buffered_data_persistency or
                 valid_buffered_data_persistency < 0):
            return (CreateChannelTuple('', 0, False, 0, 0, False),
                    ChannelBufferedDataTTLOver())

    valid_end_to_end_data_encryption = (
            form.end_to_end_data_encryption.data and False)
    # and False because not available now

    if (valid_end_to_end_data_encryption
            and not quota.end_to_end_data_encryption):
        return (CreateChannelTuple('', 0, False, 0, 0, False),
                ChannelEndToEndNotAvailable())

    return CreateChannelTuple(valid_channel_name,
                              valid_message_size,
                              valid_need_bufferization,
                              valid_buffered_message_count,
                              valid_buffered_data_persistency,
                              valid_end_to_end_data_encryption), None


def confirm_edit_channel_form(
        form: RenameChannelForm) -> (
        RenameChannelTuple, ChannelError or None):
    valid_channel_name = get_valid_channel_name(form.name.data)
    if not valid_channel_name:
        return RenameChannelTuple('', ''), ChannelNameError()

    return RenameChannelTuple(form.id.data,
                              valid_channel_name), None


def get_user_channels(user: User, session: ClassVar):
    channels = session.query(Channel) \
        .filter(Channel.owner_id == user.id).all()
    return [channel.id for channel in channels]


def create_handler(sess_cr: ClassVar,
                   limits: Callable[[int, LimitTypes], LimitDecorator]
                   ) -> Blueprint:
    """
    A closure for instantiating the handler
    that maintains channel processes.
    Must borrow a SqlAlchemy session creator for further usage.

    """

    app = Blueprint("channel", __name__)

    @app.route(ApiRoutes.CreateChannel, methods=[RequestMethods.POST])
    @limits(Limits.ChannelCreate, LimitTypes.ip)
    @limits(Limits.ChannelCreate, LimitTypes.user)
    @login_required
    def do_create_channel():
        session = sess_cr()

        channel_count = len(
            get_user_channels(current_user, session))
        user_quota: UserType = session.query(UserType).filter(
            UserType.type_id == current_user.user_type).first()

        if channel_count >= user_quota.max_channel_count:
            return make_abort(AbortResponse(
                ok=False,
                code=ChannelLimitOver.code,
                description=ChannelLimitOver.description
            ), HTTPStatus.LOCKED)

        form = RegisterChannelForm()

        (channel_name,
         max_message_size,
         need_bufferization,
         buffered_message_count,
         buffered_data_persistency,
         end_to_end_data_encryption), error = (
            confirm_create_channel_form(form, user_quota))

        if error:
            return make_abort(
                AbortResponse(ok=False,
                              code=error.code,
                              description=error.description),
                HTTPStatus.UNPROCESSABLE_ENTITY)

        channel = Channel(
            name=channel_name,
            id=generate_channel_id(),
            owner_id=current_user.id,
            max_message_size=max_message_size,
            need_bufferization=need_bufferization,
            buffered_message_count=buffered_message_count,
            buffered_data_persistency=buffered_data_persistency,
            end_to_end_data_encryption=end_to_end_data_encryption
        )

        session.add(channel)
        session.commit()
        # redis_api.add_channel(...)
        return jsonify(get_base_json_channel(channel))

    @app.route(ApiRoutes.GetChannels, methods=[RequestMethods.GET])
    @limits(Limits.GetChannels, LimitTypes.ip)
    @limits(Limits.GetChannels, LimitTypes.user)
    @login_required
    def do_get_channels():
        session = sess_cr()
        channels = session.query(Channel) \
            .filter(Channel.owner_id == current_user.id).all()
        if not channels:
            return jsonify([])

        json_channels = [get_json_channel(channel, session)
                         for channel in channels]

        return jsonify(json_channels)

    @app.route(ApiRoutes.RenameChannel, methods=[RequestMethods.PUT])
    @limits(Limits.ChannelRename, LimitTypes.ip)
    @limits(Limits.ChannelRename, LimitTypes.user)
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
