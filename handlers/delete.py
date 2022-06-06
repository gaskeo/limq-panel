#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


from typing import ClassVar

from flask import Blueprint, redirect, abort, make_response
from flask_login import current_user, login_required

from forms import DeleteKeyForm, RestrictMxForm, ToggleKeyForm
from handlers.settings import confirm_channel, ChannelMessage
from storage.channel import Channel
from storage.key import Key


def create_handler(sess_cr: ClassVar) -> Blueprint:
    """
    A closure for instantiating the handler that maintains keys and mixins delete processes.
    Must borrow a SqlAlchemy session creator for further usage.
    :param sess_cr: sqlalchemy.orm.sessionmaker object
    :return Blueprint object
    """

    app = Blueprint("delete", __name__)

    @app.route("/do/delete_key", methods=["POST"])
    @login_required
    def delete_key():
        """ Handler for deletion of keys """
        form = DeleteKeyForm()
        key_id = form.key.data

        session = sess_cr()

        key: Key = session.query(Key).filter(Key.key == key_id).first()

        if key is None:
            return abort(make_response({"message": "Bad key"}))

        channel: Channel = session.query(Channel).\
            filter(Channel.id == key.chan_id).first()

        error_message = confirm_channel(channel, current_user)
        if error_message != ChannelMessage.Ok.value:
            return abort(make_response({"message": error_message}))

        session.delete(key)
        session.commit()
        return {'key': key.key}

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

        channel_1: Channel = session.query(Channel)\
            .filter(Channel.id == subject).first()
        error_message = confirm_channel(channel_1, current_user)
        if error_message != ChannelMessage.Ok.value:
            return abort(make_response({"message": error_message}, 401))

        channel_2: Channel = session.query(Channel)\
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

        # User treats that chan_2 is scraping user's chan_1.
        # User wants to break that link

        form = RestrictMxForm()

        subject = form.subject.data
        channel_id = form.channel.data

        session = sess_cr()

        # Channels validation

        channel_1: Channel = session.query(Channel)\
            .filter(Channel.id == subject).first()

        error_message = confirm_channel(channel_1, current_user)
        if error_message != ChannelMessage.Ok.value:
            return abort(make_response({"message": error_message}, 401))

        channel_2: Channel = session.query(Channel)\
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

