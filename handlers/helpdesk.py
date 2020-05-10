#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


from flask import Blueprint, render_template


def create_handler() -> Blueprint:
    """
    A closure for instantiating the handler that maintains helpdesk processes.
    Must borrow a SqlAlchemy session creator for further usage.
    :return Blueprint object
    """

    app = Blueprint("helpdesk", __name__)

    @app.route("/helpdesk")
    def helpdesk():
        """ Main helpdesk """

        return render_template("helpdesk/helpdesk.html")

    @app.route("/helpdesk/channels_create")
    def helpdesk_ch_cr():
        """ Helpdesk for creating channels """

        return render_template("helpdesk/channels_create.html")

    @app.route("/helpdesk/channels_edit")
    def helpdesk_ch_ed():
        """ Helpdesk for editing channels """

        return render_template("helpdesk/channels_edit.html")

    @app.route("/helpdesk/keys_create")
    def helpdesk_keys_cr():
        """ Helpdesk for creating keys """

        return render_template("helpdesk/keys_create.html")

    @app.route("/helpdesk/keys_perm")
    def helpdesk_keys_pe():
        """ Key's permissions helpdesk """

        return render_template("helpdesk/keys_perm.html")

    @app.route("/helpdesk/keys_revoke")
    def helpdesk_keys_re():
        """ Helpdesk for revoke keys"""

        return render_template("helpdesk/keys_revoke.html")

    return app
