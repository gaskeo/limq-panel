#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\

from storage.db_session import base_init
from storage.user_type import UserType

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
    sess_object = base_init()
    session = sess_object()
    accounts = session.query(UserType).first()
    if accounts:
        print('db inited')
        return
    print('generate db data...')
    for user_type in USER_TYPES:
        session.add(user_type)
    session.commit()
    print('db init done')


def main():
    init_db_data()


if __name__ == "__main__":
    main()
