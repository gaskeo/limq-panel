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
    password: str


def get_params() -> Params:
    host = getenv('redis_host') or 'localhost'
    port = getenv('redis_port') or 6379
    password = getenv('redis_password') or ''
    return Params(host=host, port=port, password=password)
