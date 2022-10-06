#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\

from base64 import b64decode
from binascii import Error as DecErr

from typing import ClassVar, TypedDict, NamedTuple, Callable, List

from flask import Blueprint, request, jsonify, Response
from flask_limiter.extension import LimitDecorator
from flask_login import login_required, logout_user, login_user, \
    current_user, LoginManager
from http import HTTPStatus

from content_limits import LimitTypes, Limits
from forms import RegisterForm, LoginForm, ChangeUsernameForm, \
    ChangeEmailForm, ChangePasswordForm
from storage.keygen import generate_user_id

from storage.user import User
from storage.user_type import UserType

from . import make_abort, confirm_email, ApiRoutes, RequestMethods, \
    AbortResponse
from .errors import UserError, BadUserError, PasswordError, \
    EmailError, UsernameError, EmailExistError

MIN_PATH_LENGTH = 2
MAX_USERNAME_LENGTH = 32
MIN_PASSWORD_LENGTH = 8


class UserJson(TypedDict):
    id: str
    username: str
    email: str


class QuotaJson(TypedDict):
    name: str
    max_channel_count: int              # pcs
    max_message_size: int               # KB
    bufferization: bool
    max_bufferred_message_count: int    # pcs
    buffered_data_persistency: int      # secs
    end_to_end_data_encryption: bool


class UserResponseJson(TypedDict):
    auth: bool
    user: UserJson
    quota: QuotaJson
    path: str


class RegisterTuple(NamedTuple):
    email: str
    username: str
    password: str


class LoginTuple(NamedTuple):
    email: str
    password: str
    remember: bool


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


def get_quotas_json(quotas: UserType) -> QuotaJson:
    return QuotaJson(
        name=quotas.name,
        max_channel_count=quotas.max_channel_count,
        max_message_size=quotas.max_message_size,
        bufferization=quotas.bufferization,
        max_bufferred_message_count=quotas.max_bufferred_message_count,
        buffered_data_persistency=quotas.buffered_data_persistency,
        end_to_end_data_encryption=quotas.end_to_end_data_encryption

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
        return LoginTuple('', '', False), EmailError()

    valid_password = get_valid_password(form.password.data)
    if not valid_password:
        return LoginTuple('', '', False), PasswordError()

    return LoginTuple(
        email=valid_email,
        password=valid_password,
        remember=bool(form.remember_me.data)), None


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


def create_handler(sess_cr: ClassVar, lm: LoginManager,
                   limits: Callable[
                       [int, LimitTypes], LimitDecorator]
                   ) -> Blueprint:
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
    @limits(Limits.GetUser, LimitTypes.ip)
    @limits(Limits.GetUser, LimitTypes.user)
    def get_user():
        if current_user.is_authenticated:
            session = sess_cr()
            quotas: UserType = session.query(UserType).filter(
                UserType.type_id == current_user.user_type).first()

            return jsonify(UserResponseJson(
                auth=True, user=get_user_json(current_user),
                path='/', quota=get_quotas_json(quotas)))

        return jsonify(
            UserResponseJson(auth=False, user={}, path='/', quota={}))

    @app.route(ApiRoutes.GetQuotas, methods=[RequestMethods.GET])
    @limits(Limits.GetUser, LimitTypes.ip)
    @limits(Limits.GetUser, LimitTypes.user)
    def get_quotas():
        session = sess_cr()
        quotas: List[QuotaJson] = list(
            get_quotas_json(q) for q in session.query(UserType).all())

        return jsonify({'account_types': quotas})

    @app.route(ApiRoutes.Register, methods=[RequestMethods.POST])
    @limits(Limits.Register, LimitTypes.ip)
    @limits(Limits.Register, LimitTypes.user)
    def register():
        """ Handler for register """
        form = RegisterForm()

        (email, username, password), error = \
            confirm_register_form(form)

        if error:
            return make_abort(AbortResponse(
                ok=False,
                code=error.code,
                description=error.description
            ), HTTPStatus.UNPROCESSABLE_ENTITY)

        session = sess_cr()
        if session.query(User).filter(
                User.email == email).first():
            return make_abort(AbortResponse(
                ok=False,
                code=EmailExistError.code,
                description=EmailExistError.description
            ),
                HTTPStatus.CONFLICT)

        free = session.query(UserType)\
            .filter(UserType.name == 'Free').first()
        # noinspection PyArgumentList
        user = User(
            id=generate_user_id(),
            email=email,
            username=username,
            user_type=free.type_id
        )

        user.set_password(password)
        session.add(user)
        session.commit()

        return {"status": True, "path": "/login"}

    @app.route(ApiRoutes.Login, methods=[RequestMethods.POST])
    @limits(Limits.Login, LimitTypes.ip)
    @limits(Limits.Login, LimitTypes.user)
    def login():
        """ Handler for login """
        form = LoginForm()

        (email, password, remember), error = confirm_login_form(
            form)
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

        login_user(user, remember=remember)
        path = get_path(request.args.get("path", ''))

        return jsonify(UserResponseJson(
            auth=True, user=get_user_json(current_user),
            path=path))

    @app.route(ApiRoutes.RenameUser, methods=[RequestMethods.PUT])
    @login_required
    @limits(Limits.UserRename, LimitTypes.ip)
    @limits(Limits.UserRename, LimitTypes.user)
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
    @limits(Limits.ChangeEmail, LimitTypes.ip)
    @limits(Limits.ChangeEmail, LimitTypes.user)
    def do_change_email():
        """ E-mail changing handler. """
        form = ChangeEmailForm()

        (new_email, password), error = confirm_change_email_form(
            form)
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

        if session.query(User).filter(
                User.email == new_email).first():
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

    @app.route(ApiRoutes.ChangePassword,
               methods=[RequestMethods.PUT])
    @login_required
    @limits(Limits.ChangePassword, LimitTypes.ip)
    @limits(Limits.ChangePassword, LimitTypes.user)
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
    @limits(Limits.Logout, LimitTypes.ip)
    @limits(Limits.Logout, LimitTypes.user)
    def logout():
        """ Handler for logging out """

        logout_user()
        return {'auth': False}

    return app
