from .db_session import base_init
from typing import NamedTuple
from keygen import generate_channel_id, generate_key, generate_user_id


class User(NamedTuple):
    id: str
    email: str
    username: str
    password: str


class Channel(NamedTuple):
    id: str
    name: str
    owner_id: int


user_data = [User(generate_user_id(),
                  'a@mail.ru',
                  'user',
                  '1234567890')]

channel_data = [Channel(generate_channel_id(), 'channel 1', )]


def set_test_data():
    session = base_init()()
