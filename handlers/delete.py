from typing import ClassVar

from flask import Blueprint, redirect
from flask_login import current_user, login_required

from forms import DeleteKeyForm
from storage.channel import Channel
from storage.key import Key


def create_handler(sess_cr: ClassVar) -> Blueprint:
    app = Blueprint("delete", __name__)

    @app.route("/do/delete_key", methods=("POST",))
    @login_required
    def delete_key():
        form = DeleteKeyForm()
        key_id = form["key"].data
        sess = sess_cr()
        key: Key = sess.query(Key).filter(Key.key == key_id).first()
        if key is None:
            return redirect("/?error=bad_request")
        chan: Channel = sess.query(Channel).filter(Channel.id == key.chan_id).first()
        if chan is None:
            return redirect("/?error=bad_request")
        if chan.owner_id == current_user.id:
            sess.delete(key)
            sess.commit()
            return redirect(f"/settings/{chan.id}#list-keys-open")
        return redirect("/?error=no_access_to_this_channel")
    return app
