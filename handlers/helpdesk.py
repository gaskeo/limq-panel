#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


from typing import ClassVar

from flask import Blueprint, render_template


def create_handler(sess_cr: ClassVar) -> Blueprint:
    app = Blueprint("helpdesk", __name__)

    @app.route("/helpdesk")
    def helpdesk():
        return render_template("helpdesk/helpdesk.html")

    @app.route("/helpdesk/channels_create")
    def helpdesk_ch_cr():
        return render_template("helpdesk/channels_create.html")

    @app.route("/helpdesk/channels_edit")
    def helpdesk_ch_ed():
        return render_template("helpdesk/channels_edit.html")

    @app.route("/helpdesk/keys_create")
    def helpdesk_keys_cr():
        return render_template("helpdesk/keys_create.html")

    @app.route("/helpdesk/keys_perm")
    def helpdesk_keys_pe():
        return render_template("helpdesk/keys_perm.html")

    @app.route("/helpdesk/keys_revoke")
    def helpdesk_keys_re():
        return render_template("helpdesk/keys_revoke.html")

    return app
