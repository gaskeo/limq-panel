#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\

from flask import make_response, Flask
from flask_limiter.extension import LimitDecorator
from flask_login import current_user, AnonymousUserMixin

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from handlers import AbortResponse, errors

from typing import Callable

from enum import Enum


class Limits:
    """
    Rate limits on API methods: <count>/minute
    """

    ChannelCreate = 2
    GetChannels = 60
    ChannelRename = 3
    KeyCreate = 10
    GetKeys = 60
    KeyToggle = 10
    KeyDelete = 10
    MixinCreate = 10
    GetMixins = 60
    MixinDelete = 10
    GetUser = 60
    Register = 20
    Login = 20
    UserRename = 3
    ChangeEmail = 5
    ChangePassword = 3
    Logout = 1


def get_user_id():
    if isinstance(current_user, AnonymousUserMixin):
        user_id = get_remote_address() + LimitTypes.user.value
    else:
        user_id = current_user.id
    return user_id


class LimitTypes(Enum):
    ip = 'ip'
    user = 'user'


def init_limit(app: Flask, redis_uri: str, redis_params) -> \
        Callable[[int, LimitTypes], LimitDecorator]:
    ip_limiter = Limiter(
        app,
        key_prefix='ip',
        key_func=get_remote_address,
        storage_uri=redis_uri,
        storage_options=redis_params,
        strategy="fixed-window"
    )

    user_limiter = Limiter(
        app, key_func=lambda: get_user_id(),
        key_prefix='user',
        storage_uri=redis_uri,
        storage_options=redis_params,
        strategy="fixed-window"
    )

    def create_limit(count: int, limit_type: LimitTypes):
        if limit_type is LimitTypes.ip:
            return ip_limiter.limit(
                f"{count} per 1 minute",
                on_breach=limit_response,
                per_method=True)
        elif limit_type is LimitTypes.user:
            return user_limiter.limit(
                f"{count} per 1 minute",
                on_breach=limit_response,
                per_method=True)

    return create_limit


def limit_response(_):
    return make_response(AbortResponse(
        ok=False, code=errors.TooManyRequestsError.code,
        description=errors.TooManyRequestsError.description), 429)
