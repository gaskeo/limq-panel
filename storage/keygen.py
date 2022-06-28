#  _        _   _     _       _                       __  __  ____
# | |      (_) | |   | |     (_)                     |  \/  |/ __ \
# | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
# | |      | | | __| | '_ \  | | | | | | | '_ ` _ \  | |\/| | |  | |
# | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
# |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


# Token generation stub

import string
from secrets import choice
from typing import Iterable

USER_ID_LENGTH = 32
KEY_ID_LENGTH = 32
CHANNEL_ID_LENGTH = 16

SALT_LENGTH = 8

CHARS = string.ascii_letters + string.digits
HEX = string.digits + "abcdef"
INTS = string.digits


def get_random_string(chars: Iterable, k: int = 1) -> str:
    return "".join(choice(chars) for _ in range(k))


# Token length is 32 A-Za-z0-9 symbols.
def generate_key() -> str:
    return get_random_string(INTS, k=1) + \
           get_random_string(CHARS, k=KEY_ID_LENGTH - 1)


def generate_user_id() -> str:
    return get_random_string(CHARS, k=USER_ID_LENGTH)


def generate_salt() -> str:
    return get_random_string(CHARS, k=SALT_LENGTH)


# Generates channel's identifier
def generate_channel_id() -> str:
    return get_random_string(HEX, k=CHANNEL_ID_LENGTH)
