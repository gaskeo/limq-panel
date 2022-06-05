#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\

from base64 import b64decode
from binascii import Error as DecErr
from enum import Enum
from typing import ClassVar, TypedDict

from flask import Blueprint, request, \
    abort, Response, make_response, jsonify
from flask_login import LoginManager, login_user, current_user

from forms import LoginForm
from storage.user import User

MIN_PATH_LENGTH = 2


class UserJson(TypedDict):
    id: int
    username: str
    email: str


class UserResponseJson(TypedDict):
    auth: bool
    user: UserJson
    path: str


class FormMessage(Enum):
    Ok = ""
    EmailError = "Bad email"
    PasswordError = "Bad password"
    UserError = "Bad user"


def confirm_form(form: LoginForm) -> FormMessage:
    if not form.email.data:
        return FormMessage.EmailError.value

    if not form.password.data:
        return FormMessage.PasswordError.value

    return FormMessage.Ok.value


def get_path(encoded_path: str or bytes) -> str:
    if not encoded_path:
        return "/"
    try:
        loc = b64decode(encoded_path).decode()
        if len(loc) < MIN_PATH_LENGTH or (not loc.startswith("/")):
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
        user = session.query(User).get(user_id)
        session.close()
        return user

    @app.after_request
    def allow_cors(response: Response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    @app.route("/do/get_user", methods=["GET"])
    def get_user():
        if current_user.is_authenticated:
            return jsonify(UserResponseJson(
                auth=True,
                user=UserJson(
                    id=current_user.id,
                    username=current_user.username,
                    email=current_user.email
                ),
                path='/'))

        return jsonify(UserResponseJson(auth=False, user={}, path='/'))

    @app.route("/do/login", methods=["POST"])
    def login():
        """ Handler for login """
        form = LoginForm()
        error_message = confirm_form(form)
        if error_message != FormMessage.Ok.value:
            return abort(make_response({'message': error_message}, 400))

        session = sess_cr()
        user = session.query(
            User).filter(User.email == form.email.data).first()

        # TODO Сделать ошибки информативными
        if not user:
            return abort(make_response(
                {'message': FormMessage.UserError.value}, 403))

        if not user.check_password(form.password.data):
            return abort(make_response(
                {'message': FormMessage.PasswordError.value}, 403))

        login_user(user)

        path = get_path(request.args.get("path", None))

        return jsonify(UserResponseJson(
                auth=True,
                user=UserJson(
                    id=current_user.id,
                    username=current_user.username,
                    email=current_user.email
                ),
                path=path))

    return app
