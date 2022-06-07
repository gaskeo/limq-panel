#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\
from enum import Enum
from typing import ClassVar

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from http import HTTPStatus

from forms import CreateMixinForm, RestrictMxForm

from storage.channel import Channel
from storage.key import Key
from storage.user import User

from . import make_abort
from handlers.channel import confirm_channel, \
    ChannelMessage, get_base_json_channel
from handlers.grant import KeyMessage


class MixinMessage(Enum):
    Ok = ''
    AlreadyMixed = 'Already mixed'
    BadThread = 'Bad thread'
    BadType = 'Bad thread type'


def confirm_key_on_mixin(key: Key, channel: Channel) -> KeyMessage:
    if key is None or not key.active():
        return KeyMessage.KeyError.value

    if key.chan_id == channel.id:
        return KeyMessage.MixinError.value

    if not key.can_read():
        return KeyMessage.WrongPermissionError.value

    return KeyMessage.Ok.value


StatusCode = int


def confirm_channels(channel_1: Channel, channel_2: Channel, user: User,
                     ) -> (ChannelMessage, StatusCode):
    error_message = confirm_channel(channel_1, user)
    if error_message != ChannelMessage.Ok.value:
        return error_message, HTTPStatus.FORBIDDEN

    if channel_2 is None:
        return ChannelMessage.ChannelNotExistError.value, \
               HTTPStatus.BAD_REQUEST
    return ChannelMessage.Ok.value, 200


def confirm_restrict_mixin_form(form: RestrictMxForm) -> MixinMessage:
    if not form.channel or not form.subject:
        return MixinMessage.BadThread.value

    if form.mixin_type not in ("in", "out"):
        return MixinMessage.BadType.value

    return MixinMessage.Ok.value


def create_handler(sess_cr: ClassVar) -> Blueprint:
    app = Blueprint("mixin", __name__)

    @app.route("/do/get_mixins", methods=["GET"])
    @login_required
    def do_get_mixins():
        channel_id = request.args.get('channel_id', '')
        if not channel_id:
            make_abort(ChannelMessage.ChannelNotExistError,
                       HTTPStatus.UNPROCESSABLE_ENTITY)

        session = sess_cr()

        channel: Channel = session.query(Channel). \
            filter(Channel.id == channel_id).first()

        error_message = confirm_channel(channel, current_user)
        if error_message != ChannelMessage.Ok.value:
            return make_abort(error_message, HTTPStatus.FORBIDDEN)

        mixin_out = \
            tuple(session.query(Channel)
                  .filter(Channel.id == id_channel).first()
                  for id_channel in channel.mixins())

        mixin_in = tuple(session.query(Channel).filter(
            Channel.forwards.like(f"%{channel.id}%")).all())

        mixin_out_json = [
            get_base_json_channel(channel) for channel in mixin_out]

        mixin_in_json = [
            get_base_json_channel(channel) for channel in mixin_in
        ]

        return jsonify({'in': mixin_in_json, 'out': mixin_out_json})

    @app.route("/do/create_mixin", methods=["POST"])
    @login_required
    def do_create_mixin():
        """ Handler for mixin creating. """

        form = CreateMixinForm()
        channel = form.channel.data
        mix_key = form.key.data
        session = sess_cr()

        # Key and channel validation

        channel = session.query(Channel).filter(
            Channel.id == channel).first()

        error_message = confirm_channel(channel, current_user)
        if error_message != ChannelMessage.Ok.value:
            return make_abort(error_message, HTTPStatus.FORBIDDEN)

        key = session.query(Key).filter(Key.key == mix_key).first()
        error_message = confirm_key_on_mixin(key, channel)

        if error_message != KeyMessage.Ok.value:
            return make_abort(error_message, HTTPStatus.FORBIDDEN)

        src_channel = session.query(Channel).filter(
            Channel.id == key.chan_id).first()

        mixins = list(src_channel.mixins())

        if channel.id in mixins:
            return make_abort(MixinMessage.AlreadyMixed.value,
                              HTTPStatus.BAD_REQUEST)

        mixins.append(channel.id)
        src_channel.update_mixins(mixins)

        session.commit()

        return {"mixin": get_base_json_channel(src_channel)}

    @app.route("/do/restrict_mx", methods=["POST"])
    @login_required
    def restrict_out_mx():
        """ Handler for restriction of outgoing mixin. """

        # User treats that channel_2 is scraping user's channel_1.
        # User wants to break that link

        form = RestrictMxForm()

        error_message = confirm_restrict_mixin_form(form)
        if error_message != MixinMessage.Ok.value:
            return make_abort(error_message,
                              HTTPStatus.UNPROCESSABLE_ENTITY)

        subject = form.subject.data
        channel_id = form.channel.data

        session = sess_cr()

        channel_1 = session.query(Channel) \
            .filter(Channel.id == subject).first()
        channel_2 = session.query(Channel) \
            .filter(Channel.id == channel_id).first()

        error_message, code = \
            confirm_channels(channel_1, channel_2, current_user)
        if error_message != ChannelMessage.Ok.value:
            return make_abort(error_message, code)

        if form.mixin_type == "out":
            mx = list(channel_1.mixins())
            if channel_2.id not in mx:
                return make_abort(MixinMessage.BadThread.value,
                                  HTTPStatus.BAD_REQUEST)

            mx.remove(channel_2.id)
            channel_1.update_mixins(mx)
            session.commit()

        else:
            mx = list(channel_2.mixins())

            if channel_1.id not in mx:
                return make_abort(MixinMessage.BadThread.value,
                                  HTTPStatus.BAD_REQUEST)

            mx.remove(channel_1.id)
            channel_2.update_mixins(mx)
            session.commit()

        return {'mixin': channel_2.id}

    return app
