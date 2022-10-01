#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\

from base64 import b64encode

from flask import redirect, Blueprint, request

app = Blueprint("errors", __name__)


@app.errorhandler(401)
def error_401(_):
    """
    Handler for 401 error.
    When unauthorized, just goto login page.

    """

    return redirect("/login?path=" + b64encode(request.path.encode()).decode())
