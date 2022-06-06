from typing import ClassVar

from flask import Blueprint, jsonify, request, abort, make_response
from flask_login import current_user, login_required

from handlers.get_channels import get_base_json_channel
from handlers.settings import confirm_channel, ChannelMessage
from storage.channel import Channel


def create_handler(sess_cr: ClassVar) -> Blueprint:
    app = Blueprint("get_mixins", __name__)

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

    return app
