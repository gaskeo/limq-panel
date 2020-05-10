#  _        _   _     _       _                       __  __  ____
# | |      (_) | |   | |     (_)                     |  \/  |/ __ \
# | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
# | |      | | | __| | '_ \  | | | | | | | '_ ` _ \  | |\/| | |  | |
# | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
# |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


# Token generation stub

import random

LENGTH = 32
CHAN_ID_LENGTH = 16

CHARS = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"


# Token length is 32 A-Za-z0-9 symbols.
def generate_key() -> str:
    return str(random.getrandbits(3)) + "".join(random.choices(CHARS, k=LENGTH - 1))


# Generates channel's identifier
def chan_identifier() -> str:
    return f"{random.getrandbits(64):x}"

