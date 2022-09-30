from flask import make_response, Flask
from flask_limiter.extension import LimitDecorator
from flask_login import current_user

from flask_limiter import Limiter, RequestLimit
from flask_limiter.util import get_remote_address
from handlers import AbortResponse

from typing import Callable

from enum import Enum


class Limits:
    ChannelCreate = 2
    ChannelRename = 3
    KeyCreate = 10
    KeyToggle = 10
    KeyDelete = 10
    MixinCreate = 10


def get_user_id():
    return current_user.id


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


def limit_response(request_limit: RequestLimit):
    return make_response(AbortResponse(
        ok=False, code=1100,
        description=f'too many requests. '
                    f'Available {request_limit.limit}'), 429)
