#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\

from base64 import b64decode
from binascii import Error as DecErr
from typing import ClassVar

from flask import Blueprint, request, abort
from flask_login import LoginManager, login_user, current_user

from forms import LoginForm
from storage.user import User


def get_path(encoded_path: str or bytes) -> str:
    if not encoded_path:
        return "/"
    try:
        loc = b64decode(encoded_path).decode()
        if len(loc) < 2 or (not loc.startswith("/")):
            return "/"
        return loc
    except (DecErr, UnicodeDecodeError):
        return "/"


def create_handler(sess_cr: ClassVar, lm: LoginManager) -> Blueprint:
    """
    A closure for instantiating the handler that maintains login process.
    Must borrow a SqlAlchemy session creator for further usage.
    :param lm: login manager
    :param sess_cr: sqlalchemy.orm.sessionmaker object
    :return Blueprint object
    """

    app = Blueprint("login", __name__)

    @lm.user_loader
    def load_user(user_id: int):
        """ Function for loading the user """

        session = sess_cr()
        u = session.query(User).get(user_id)
        session.close()
        return u

    @app.after_request
    def response(res):
        res.headers['Access-Control-Allow-Origin'] = '*'
        return res

    @app.route("/do/get_user", methods=["GET"])
    def get_user():
        if current_user.is_authenticated:
            return {'auth': True, 'user': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email
            }}
        return {'auth': False, 'user': None}

    @app.route("/do/login", methods=["POST"])
    def login():
        """ Handler for login """
        form = LoginForm()

        # User validation
        sess = sess_cr()
        user = sess.query(
            User).filter(User.email == form.email.data).first()

        # TODO Сделать ошибки информативными
        if not user:
            return abort(403)
        if not user.check_password(form.password.data):
            return abort(403)

        login_user(user)

        path = get_path(request.args.get("path", None))

        return {"auth": True, "user": {
            "email": user.email,
            "username": user.username,
            "id": user.id
        }, "path": path}

    return app
