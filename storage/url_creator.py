#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\

from os import getenv

PSQL_USER = getenv('psql_user') or 'limq_front'
PSQL_PASSWORD = getenv('psql_password')
PSQL_ADDRESS = getenv('psql_host') or 'localhost'
PSQL_PORT = getenv('psql_port') or '5432'
PSQL_DB = getenv('psql_db') or 'limq'


def create_url():
    return f"postgresql://{PSQL_USER}:{PSQL_PASSWORD}@" \
           f"{PSQL_ADDRESS}:{PSQL_PORT}/{PSQL_DB}"
