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
