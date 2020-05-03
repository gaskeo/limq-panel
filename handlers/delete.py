from typing import ClassVar

from flask import Blueprint, redirect
from flask_login import current_user, login_required

from forms import DeleteKeyForm, RestrictMxForm
from storage.channel import Channel
from storage.key import Key


def create_handler(sess_cr: ClassVar) -> Blueprint:
    app = Blueprint("delete", __name__)

    @app.route("/do/delete_key", methods=("POST",))
    @login_required
    def delete_key():
        form = DeleteKeyForm()

        if not form.validate():
            return redirect("/?error=bad_request")

        key_id = form.key.data

        sess = sess_cr()

        key: Key = sess.query(Key).filter(Key.key == key_id).first()

        if key is None:
            return redirect("/?error=bad_request")

        chan: Channel = sess.query(Channel).filter(Channel.id == key.chan_id).first()

        if chan is None:
            return redirect("/?error=bad_request")

        if chan.owner_id != current_user.id:
            return redirect("/?error=no_access_to_this_channel")

        sess.delete(key)
        sess.commit()
        return redirect(f"/settings/{chan.id}#list-keys-open")

    @app.route("/do/restrict_in_mx", methods=("POST",))
    @login_required
    def restrict_in_mx():
        # User treats that their chan_1 is scraping messages from chan_2. He wants to break that link

        form = RestrictMxForm()

        if not form.validate():
            return redirect("/?error=bad_request")

        subject = form.subject.data
        chan = form.chan.data

        sess = sess_cr()

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
        # User treats that chan_2 is scraping user's chan_1. User wants to break that link

        form = RestrictMxForm()

        if not form.validate():
            return redirect("/?error=bad_request")

        subject = form.subject.data
        chan = form.chan.data

        sess = sess_cr()

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

    return app

