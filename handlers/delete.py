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

        if not form.validate():
            return redirect("/?error=bad_request")

        subject = form.subject.data
        chan = form.chan.data

        sess = sess_cr()

        # Channels validation

        chan_1: Channel = sess.query(Channel).filter(Channel.id == subject).first()
        if chan_1 is None:
            return redirect("/?error=bad_request")

        chan_2: Channel = sess.query(Channel).filter(Channel.id == chan).first()
        if chan_2 is None:
            return redirect("/?error=bad_request")

        if not chan_1.owner_id == current_user.id:
            return redirect("/?error=no_access_to_this_channel")

        mx = list(chan_2.mixins())
        if chan_1.id not in mx:
            return redirect("/?error=invalid_treat")
        mx.remove(chan_1.id)

        chan_2.update_mixins(mx)

        sess.commit()

        return redirect(f"/settings/{chan_1.id}#list-mixin-settings-open")

    @app.route("/do/restrict_out_mx", methods=("POST",))
    @login_required
    def restrict_out_mx():
        """ Handler for restriction of outcoming mixin. """

        # User treats that chan_2 is scraping user's chan_1. User wants to break that link

        form = RestrictMxForm()

        if not form.validate():
            return redirect("/?error=bad_request")

        subject = form.subject.data
        chan = form.chan.data

        sess = sess_cr()

        # Channels validation

        chan_1: Channel = sess.query(Channel).filter(Channel.id == subject).first()
        if chan_1 is None:
            return redirect("/?error=bad_request")

        chan_2: Channel = sess.query(Channel).filter(Channel.id == chan).first()
        if chan_2 is None:
            return redirect("/?error=bad_request")

        if not chan_1.owner_id == current_user.id:
            return redirect("/?error=no_access_to_this_channel")

        mx = list(chan_1.mixins())
        if chan_2.id not in mx:
            return redirect("/?error=invalid_treat")
        mx.remove(chan_2.id)

        chan_1.update_mixins(mx)

        sess.commit()

        return redirect(f"/settings/{chan_1.id}#list-mixin-settings-open")

    @app.route("/do/toggle_key", methods=("POST",))
    @login_required
    def toggle_key():
        """ Handler for toggling a key's active state. """

        sess = sess_cr()

        form = ToggleKeyForm()

        if not form.validate():
            return redirect("/?error=bad_request")

        # Key and channel validations

        key_val = form.key.data
        key: Key = sess.query(Key).filter(Key.key == key_val).first()

        if key is None:
            return redirect("/?error=bad_request")

        chan: Channel = sess.query(Channel).filter(Channel.id == key.chan_id).first()

        if chan is None:
            return redirect("/?error=bad_request")

        if chan.owner_id != current_user.id:
            return redirect("/?error=no_access_to_this_channel")

        key.toggle_active()

        sess.commit()
        return redirect(f"/settings/{chan.id}#list-keys-open")

    return app

