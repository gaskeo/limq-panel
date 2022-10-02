#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\

import sqlalchemy

from .db_session import ModelBase


class UserType(ModelBase):
    """
    SqlAlchemy-integrated user type descriptor.
    """

    __tablename__ = 'user_types'

    type_id = sqlalchemy.Column(sqlalchemy.Integer,
                                primary_key=True, autoincrement=True)

    name = sqlalchemy.Column(sqlalchemy.String(length=32))
    max_channel_count = sqlalchemy.Column(sqlalchemy.Integer,
                                          nullable=False)
    max_message_size = sqlalchemy.Column(sqlalchemy.Integer,
                                         nullable=False)
    bufferization = sqlalchemy.Column(sqlalchemy.Boolean,
                                      nullable=False)

    max_bufferred_message_count = sqlalchemy.Column(sqlalchemy.Integer,
                                                    nullable=False)

    buffered_data_persistency = sqlalchemy.Column(sqlalchemy.Integer,
                                                  nullable=False)

    end_to_end_data_encryption = sqlalchemy.Column(sqlalchemy.Boolean,
                                                   nullable=False)
