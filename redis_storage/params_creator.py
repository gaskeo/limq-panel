#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\

from typing import TypedDict
from os import getenv


class Params(TypedDict):
    host: str
    port: int
    db: int
    password: str


def get_params() -> Params:
    host = getenv('redis_host') or 'localhost'
    port = int(getenv('redis_port')) \
        if getenv('redis_port') and getenv('redis_port').isdigit() \
        else 6379

    db = int(getenv('redis_db')) if \
        getenv('redis_db') and getenv('redis_db').isdigit() else 3
    password = getenv('redis_password') or ''

    return Params(host=host, port=port, db=db, password=password)


def get_limits_params() -> Params:
    host = getenv('redis_limit_host') or 'localhost'
    port = int(getenv('redis_limit_port')) if \
        getenv('redis_limit_port') and \
        getenv('redis_limit_port').isdigit() \
        else 6379

    db = int(getenv('redis_limit_db')) if \
        getenv('redis_limit_db') and \
        getenv('redis_limit_db').isdigit() else 4
    password = getenv('redis_limit_password') or ''

    return Params(host=host, port=port, db=db, password=password)


redis_uri = str


def get_redis_link() -> (redis_uri, Params):
    redis_params = get_limits_params()
    storage_uri = f"redis://{redis_params['host']}:" \
                  f"{redis_params['port']}"

    return storage_uri, redis_params
