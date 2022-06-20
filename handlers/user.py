#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\

from base64 import b64decode
from binascii import Error as DecErr

from typing import ClassVar, TypedDict, NamedTuple

from flask import Blueprint, request, jsonify, Response
from flask_login import login_required, logout_user, login_user, \
    current_user, LoginManager
from http import HTTPStatus

from forms import RegisterForm, LoginForm, ChangeUsernameForm, \
    ChangeEmailForm, ChangePasswordForm
from storage.keygen import generate_user_id

from storage.user import User

from . import make_abort, confirm_email, ApiRoutes, RequestMethods, \
    AbortResponse
from .errors import UserError, BadUserError, PasswordError,\
    EmailError, UsernameError, EmailExistError

MIN_PATH_LENGTH = 2
MAX_USERNAME_LENGTH = 32
MIN_PASSWORD_LENGTH = 8


class UserJson(TypedDict):
    id: str
    username: str
    email: str


class UserResponseJson(TypedDict):
    auth: bool
    user: UserJson
    path: str


class RegisterTuple(NamedTuple):
    email: str
    username: str
    password: str


class LoginTuple(NamedTuple):
    email: str
    password: str


class ChangeEmailTuple(NamedTuple):
    new_email: str
    password: str


class ChangePasswordTuple(NamedTuple):
    old_password: str
    new_password: str


def get_path(encoded_path: str or bytes or None) -> str:
    if not encoded_path:
        return "/"
    try:
        loc = b64decode(encoded_path).decode()
        if len(loc) < MIN_PATH_LENGTH or (not loc.startswith("/")):
            return "/"
        return loc
    except (DecErr, UnicodeDecodeError):
        return "/"


def get_user_json(user: User) -> UserJson:
    return UserJson(
        id=user.id,
        username=user.username,
        email=user.email
    )


def confirm_user(user: User, password: str) -> UserError or None:
    if not user:
        return BadUserError()

    if not user.check_password(password):
        return PasswordError()

    return


def get_valid_email(email: str or None) -> str:
    if not email:
        return ''
    return confirm_email(email)


def get_valid_username(username: str or None) -> str:
    if not username:
        return ''

    username = username.strip()
    if len(username) > MAX_USERNAME_LENGTH or not len(username):
        return ''
    return username


def get_valid_password(password: str or None) -> str:
    if not password:
        return ''
    password = password.strip()
    if len(password) < MIN_PASSWORD_LENGTH or not len(password):
        return ''
    return password


def confirm_register_form(form: RegisterForm) -> \
        (RegisterTuple, UserError or None):
    valid_email = get_valid_email(form.email.data)
    if not valid_email:
        return RegisterTuple('', '', ''), EmailError()

    valid_username = get_valid_username(form.username.data)
    if not valid_username:
        return RegisterTuple('', '', ''), UsernameError()

    valid_password = get_valid_password(form.password.data)
    if not valid_password:
        return RegisterTuple('', '', ''), PasswordError()

    return RegisterTuple(
        email=valid_email,
        username=valid_username,
        password=valid_password), None


def confirm_login_form(form: LoginForm) -> \
        (LoginTuple, UserError or None):
    valid_email = get_valid_email(form.email.data)
    if not valid_email:
        return LoginTuple('', ''), EmailError()

    valid_password = get_valid_password(form.password.data)
    if not valid_password:
        return LoginTuple('', ''), PasswordError()

    return LoginTuple(
        email=valid_email,
        password=valid_password), None


def confirm_change_email_form(form: ChangeEmailForm) -> \
        (ChangeEmailTuple, UserError or None):
    valid_email = get_valid_email(form.new_email.data)
    if not valid_email:
        return ChangeEmailTuple('', ''), EmailError()

    valid_password = get_valid_password(form.password.data)
    if not valid_password:
        return ChangeEmailTuple('', ''), PasswordError()

    return ChangeEmailTuple(
        new_email=valid_email,
        password=valid_password), None


def confirm_change_password_form(form: ChangePasswordForm) -> \
        (ChangePasswordTuple, UserError or None):
    valid_old_password = get_valid_password(form.old_password.data)
    if not valid_old_password:
        return ChangePasswordTuple('', ''), PasswordError()

    valid_new_password = get_valid_password(form.password.data)
    if not valid_new_password:
        return ChangePasswordTuple('', ''), PasswordError()
    return ChangePasswordTuple(
        old_password=valid_old_password,
        new_password=valid_new_password), None


def create_handler(sess_cr: ClassVar, lm: LoginManager) -> Blueprint:
    """
    A closure for instantiating the handler
    that maintains user processes.
    Must borrow a SqlAlchemy session creator for further usage.

    """

    app = Blueprint("user", __name__)

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

    @app.route(ApiRoutes.GetUser, methods=[RequestMethods.GET])
    def get_user():
        if current_user.is_authenticated:
            return jsonify(UserResponseJson(
                auth=True, user=get_user_json(current_user),
                path='/'))

        return jsonify(UserResponseJson(auth=False, user={}, path='/'))

    @app.route(ApiRoutes.Register, methods=[RequestMethods.POST])
    def register():
        """ Handler for register """
        form = RegisterForm()

        session = sess_cr()
        (email, username, password), error = \
            confirm_register_form(form)

        if error:
            return make_abort(AbortResponse(
                ok=False,
                code=error.code,
                description=error.description
            ), HTTPStatus.UNPROCESSABLE_ENTITY)

        if session.query(User).filter(
                User.email == email).first():
            return make_abort(AbortResponse(
                ok=False,
                code=EmailExistError.code,
                description=EmailExistError.description
            ),
                HTTPStatus.CONFLICT)

        # noinspection PyArgumentList
        user = User(
            id=generate_user_id(),
            email=email,
            username=username
        )

        user.set_password(password)
        session.add(user)
        session.commit()

        return {"status": True, "path": "/login"}

    @app.route(ApiRoutes.Login, methods=[RequestMethods.POST])
    def login():
        """ Handler for login """
        form = LoginForm()

        (email, password), error = confirm_login_form(form)
        if error:
            return make_abort(AbortResponse(
                ok=False,
                code=error.code,
                description=error.description
            ),
                HTTPStatus.UNPROCESSABLE_ENTITY)

        session = sess_cr()
        user = session.query(
            User).filter(User.email == email).first()

        error = confirm_user(user, password)
        if error:
            return make_abort(AbortResponse(
                ok=False,
                code=error.code,
                description=error.description
            ), HTTPStatus.FORBIDDEN)

        login_user(user)
        path = get_path(request.args.get("path", ''))

        return jsonify(UserResponseJson(
            auth=True, user=get_user_json(current_user),
            path=path))

    @app.route(ApiRoutes.RenameUser, methods=[RequestMethods.PUT])
    @login_required
    def do_change_username():
        form = ChangeUsernameForm()

        username = get_valid_username(form.new_username.data)
        if not username:
            return make_abort(AbortResponse(
                ok=False,
                code=UsernameError.code,
                description=UsernameError.description
            ),
                HTTPStatus.UNPROCESSABLE_ENTITY)

        session = sess_cr()

        user = session.query(User).filter(
            User.id == current_user.id).first()
        if not user:
            return make_abort(AbortResponse(
                ok=False,
                code=BadUserError.code,
                description=BadUserError.description
            ), HTTPStatus.UNPROCESSABLE_ENTITY)

        user.username = username
        session.commit()
        return jsonify(UserResponseJson(
            auth=True, user=get_user_json(user), path=''))

    @app.route(ApiRoutes.ChangeEmail, methods=[RequestMethods.PUT])
    @login_required
    def do_change_email():
        """ E-mail changing handler. """
        form = ChangeEmailForm()

        (new_email, password), error = confirm_change_email_form(form)
        if error:
            return make_abort(AbortResponse(
                ok=False,
                code=error.code,
                description=error.description
            ), HTTPStatus.UNPROCESSABLE_ENTITY)

        session = sess_cr()

        user = session.query(User).filter(
            User.id == current_user.id).first()

        error = confirm_user(user, password)
        if error:
            return make_abort(AbortResponse(
                ok=False,
                code=error.code,
                description=error.description
            ),
                HTTPStatus.FORBIDDEN)

        if session.query(User).filter(User.email == new_email).first():
            return make_abort(AbortResponse(
                ok=False,
                code=EmailExistError.code,
                description=EmailExistError.description
            ),
                HTTPStatus.CONFLICT)

        user.email = new_email
        session.commit()

        return jsonify(UserResponseJson(auth=True,
                                        user=get_user_json(user),
                                        path=''))

    @app.route(ApiRoutes.ChangePassword, methods=[RequestMethods.PUT])
    @login_required
    def do_change_password():
        """ Password changing handler. """

        form = ChangePasswordForm()

        (old_password, new_password), message = \
            confirm_change_password_form(form)

        session = sess_cr()

        # User validation

        user = session.query(User).filter(
            User.id == current_user.id).first()

        error = confirm_user(user, old_password)
        if error:
            return make_abort(AbortResponse(
                ok=False,
                code=error.code,
                description=error.description
            ), HTTPStatus.FORBIDDEN)

        user.set_password(new_password)

        session.commit()
        return jsonify(UserResponseJson(auth=True,
                                        user=get_user_json(user),
                                        path=''))

    @app.route(ApiRoutes.Logout, methods=[RequestMethods.POST])
    @login_required
    def logout():
        """ Handler for logging out """

        logout_user()
        return {'auth': False}

    return app
