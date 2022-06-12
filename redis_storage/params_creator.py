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
