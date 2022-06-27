#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\

from flask import Blueprint, render_template
from . import RequestMethods


def create_handler() -> Blueprint:
    """
    A closure for instantiating the handler
    that maintains mainpage.
    Must borrow a SqlAlchemy session creator for further usage.
    """

    app = Blueprint("index", __name__)

    @app.route("/", methods=[RequestMethods.GET])
    def index():
        """ Handler for main page """
        return render_template("index.html")

    return app
