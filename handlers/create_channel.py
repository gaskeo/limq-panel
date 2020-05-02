#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


from typing import ClassVar

from flask import Blueprint, render_template, redirect
from flask_login import current_user, login_required

from forms import RegisterChannelForm
from storage.channel import Channel
from storage.keygen import chan_identifier


def create_handler(sess_cr: ClassVar) -> Blueprint:
    app = Blueprint("create_channel", __name__)

    @app.route("/create_channel", methods=["GET", "POST"])
    def create_channel():
        form = RegisterChannelForm()
        param = {"name_site": "Lithium MQ", "title": "Регистрация канала", "form": form}
        return render_template("create_channel.html", **param)

    @app.route("/do/create_channel", methods=("POST",))
    @login_required
    def do_create_channel():
        form = RegisterChannelForm()

        session = sess_cr()
        channel = Channel(
            name=form.name.data,
            is_active=True,
            id=chan_identifier(),
            owner_id=current_user.id
        )
        session.add(channel)
        session.commit()
        return redirect("/")

    return app
