from typing import ClassVar

from flask import Blueprint, jsonify, request, abort, make_response
from flask_login import current_user, login_required

from forms import CreateMixinForm, RestrictMxForm
from handlers.channel import confirm_channel, \
    ChannelMessage, get_base_json_channel
from handlers.grant import KeyMessage
from storage.channel import Channel
from storage.key import Key


def confirm_key_on_mixin(key: Key, channel: Channel) -> KeyMessage:
    if key is None or not key.active():
        return KeyMessage.KeyError.value

    if key.chan_id == channel.id:
        return KeyMessage.MixinError.value

    if not key.can_read():
        return KeyMessage.WrongPermissionError.value

    return KeyMessage.Ok.value


def create_handler(sess_cr: ClassVar) -> Blueprint:
    app = Blueprint("mixin", __name__)

    @app.route("/do/get_mixins", methods=["GET"])
    @login_required
    def do_get_mixins():
        channel_id = request.args.get('channel_id', None)

        session = sess_cr()

        channel: Channel = session.query(Channel). \
            filter(Channel.id == channel_id).first()

        error_message = confirm_channel(channel, current_user)
        if error_message != ChannelMessage.Ok.value:
            return abort(make_response({'message': error_message}, 401))

        mixin_out = \
            tuple(session.query(Channel)
                  .filter(Channel.id == id_channel).first()
                  for id_channel in channel.mixins())

        mixin_in = tuple(session.query(Channel).filter(
            Channel.forwards.like(f"%{channel.id}%")).all())

        mixin_out_json = []
        for other_channel in mixin_out:
            mixin_out_json.append(get_base_json_channel(other_channel))

        mixin_in_json = []
        for other_channel in mixin_in:
            mixin_in_json.append(get_base_json_channel(other_channel))

        return jsonify({'in': mixin_in_json, 'out': mixin_out_json})

    @app.route("/do/create_mixin", methods=("POST",))
    @login_required
    def do_create_mixin():
        """ Handler for mixin creating. """

        form = CreateMixinForm()
        channel: str = form.channel.data
        mix_key: str = form.key.data
        sess = sess_cr()

        # Key and channel validation

        channel: Channel = sess.query(Channel).filter(
            Channel.id == channel).first()

        error_message = confirm_channel(channel, current_user)
        if error_message != ChannelMessage.Ok.value:
            return abort(make_response({"message": error_message}, 401))

        key: Key = sess.query(Key).filter(Key.key == mix_key).first()
        error_message = confirm_key_on_mixin(key, channel)

        if error_message != KeyMessage.Ok.value:
            return abort(make_response({"message": error_message}, 401))

        src_channel: Channel = sess.query(Channel).filter(
            Channel.id == key.chan_id).first()

        mixins = list(src_channel.mixins())

        if channel.id in mixins:
            return abort(
                make_response({"message": "already mixed"}, 400))

        mixins.append(channel.id)
        src_channel.update_mixins(mixins)

        sess.commit()

        return {"mixin": get_base_json_channel(src_channel)}

    @app.route("/do/restrict_in_mx", methods=("POST",))
    @login_required
    def restrict_in_mx():
        """ Handler for restriction of incoming mixin. """

        # User treats that their channel_1
        # is scraping messages from channel_2.
        # He wants to break that link

        form = RestrictMxForm()

        subject = form.subject.data
        channel_id = form.channel.data

        session = sess_cr()

        # Channels validation

        channel_1: Channel = session.query(Channel) \
            .filter(Channel.id == subject).first()
        error_message = confirm_channel(channel_1, current_user)
        if error_message != ChannelMessage.Ok.value:
            return abort(make_response({"message": error_message}, 401))

        channel_2: Channel = session.query(Channel) \
            .filter(Channel.id == channel_id).first()

        if channel_2 is None:
            return abort(make_response(
                {"message": ChannelMessage.ChannelNotExistError.value},
                400))

        mx = list(channel_2.mixins())
        if channel_1.id not in mx:
            return abort(make_response(
                {"message": "Bad Thread"},
                400))

        mx.remove(channel_1.id)

        channel_2.update_mixins(mx)

        session.commit()

        return {'mixin': channel_2.id}

    @app.route("/do/restrict_out_mx", methods=("POST",))
    @login_required
    def restrict_out_mx():
        """ Handler for restriction of outcoming mixin. """

        # User treats that channel_2 is scraping user's channel_1.
        # User wants to break that link

        form = RestrictMxForm()

        subject = form.subject.data
        channel_id = form.channel.data

        session = sess_cr()

        # Channels validation

        channel_1: Channel = session.query(Channel) \
            .filter(Channel.id == subject).first()

        error_message = confirm_channel(channel_1, current_user)
        if error_message != ChannelMessage.Ok.value:
            return abort(make_response({"message": error_message}, 401))

        channel_2: Channel = session.query(Channel) \
            .filter(Channel.id == channel_id).first()
        if channel_2 is None:
            return abort(make_response(
                {"message": ChannelMessage.ChannelNotExistError.value},
                400))

        mx = list(channel_1.mixins())
        if channel_2.id not in mx:
            return abort(make_response(
                {"message": "Bad Thread"},
                400))

        mx.remove(channel_2.id)

        channel_1.update_mixins(mx)

        session.commit()

        return {'mixin': channel_2.id}

    return app
