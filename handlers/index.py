#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


from typing import ClassVar

from flask import Blueprint, render_template, request, redirect
from flask_login import current_user, login_required, logout_user

from errors import explain as explain_error
from forms import RegisterForm
from storage.channel import Channel
from storage.key import Key
from storage.user import User


def create_handler(sess_cr: ClassVar) -> Blueprint:
    """
    A closure for instantiating the handler that maintains mainpage.
    Must borrow a SqlAlchemy session creator for further usage.
    :param sess_cr: sqlalchemy.orm.sessionmaker object
    :return Blueprint object
    """

    app = Blueprint("index", __name__)

    @app.route("/", methods=["GET", "POST"])
    def index():
        """ Handler for main page """
        return render_template("mainpage.html")

    @app.route("/logout")
    @login_required
    def logout():
        """ Handler for logging out """

        logout_user()
        return redirect("/")

    return app
