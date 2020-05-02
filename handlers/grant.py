#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


from datetime import datetime
from typing import ClassVar

from flask import Blueprint, render_template, redirect, request
from flask_login import current_user, login_required

from forms import CreateKeyForm
from storage.channel import Channel
from storage.key import Key
from storage.keygen import generate_key


def create_handler(sess_cr: ClassVar) -> Blueprint:
    app = Blueprint("grant", __name__)

    @app.route("/grant")
    @login_required
    def grant():
        f = CreateKeyForm()
        uid = current_user.id
        sess = sess_cr()

        channels = sess.query(Channel).filter(Channel.owner_id == uid).all()

        return render_template("create_key.html", form=f, channels=channels)

    @app.route("/do/grant", methods=("POST",))
    @login_required
    def do_grant():
        form = CreateKeyForm(request.form)

        if not form.validate():
            return redirect("/?error=bad_request")
        sess = sess_cr()

        channel = form.id.data

        chan: Channel = sess.query(Channel).filter(Channel.id == channel).first()
        if not chan:
            return redirect("/?error=channel_invalid")

        if chan.owner_id != current_user.id:
            return redirect("/?error=no_access_to_this_channel")

        key_s = generate_key()
        key = Key(key=key_s, chan_id=channel, name=form.name.data, created=datetime.now())

        perm = form.permissions.data
        if perm not in "01":
            return redirect("/?error=wrong_permissions")

        read = perm == "0"
        write = read ^ 1

        info = form.info_allowed.data

        key.perm = info << 2 | write << 1 | read
        sess.add(key)

        sess.commit()

        return redirect(f"/settings/{channel}#list-keys-open")

    return app
