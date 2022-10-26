#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\
import psycopg2
import logging

import sqlalchemy

from storage.db_session import base_init
from storage.user_type import UserType

FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
logging.basicConfig(format=FORMAT)

# TODO in json or something else
USER_TYPES = [
    UserType(
        name='Free',
        max_channel_count=2,
        max_message_size=256,
        bufferization=True,
        max_bufferred_message_count=256,
        buffered_data_persistency=12,
        end_to_end_data_encryption=False
    )
]


# init data in tables
def init_db_data():
    while True:
        try:
            sess_object = base_init()
            break
        except sqlalchemy.exc.OperationalError:
            logging.warning('DB host is down. Reconnect...')
        except Exception as e:
            logging.warning('Unknown error on connecting to DB. '
                            'Reconnect...')

    logging.info('Connected to DB')

    session = sess_object()
    accounts = session.query(UserType).first()
    if accounts:
        logging.info('DB has already been initialized')
        return
    logging.info('Insert data in DB')
    for user_type in USER_TYPES:
        session.add(user_type)
    session.commit()
    logging.info('DB init done')


def main():
    init_db_data()


if __name__ == "__main__":
    main()
