#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\

import sqlalchemy

from .db_session import ModelBase


class Channel(ModelBase):
    """
    SqlAlchemy-integrated channel descriptor.
    Has special methods for mixin management.
    """

    __tablename__ = 'channels'

    name = sqlalchemy.Column(sqlalchemy.String(length=64),
                             nullable=False)

    id = sqlalchemy.Column(sqlalchemy.String(length=16),
                           nullable=False,
                           primary_key=True,
                           unique=True)

    owner_id = sqlalchemy.Column(sqlalchemy.String,
                                 sqlalchemy.ForeignKey("users.id"),
                                 nullable=False)

    max_message_size = sqlalchemy.Column(sqlalchemy.Integer, default=1)
    need_bufferization = sqlalchemy.Column(sqlalchemy.Boolean,
                                           default=False)
    buffered_message_count = sqlalchemy.Column(sqlalchemy.Integer,
                                               default=0)
    buffered_data_persistency = sqlalchemy.Column(sqlalchemy.Integer,
                                                  default=0)
    end_to_end_data_encryption = sqlalchemy.Column(sqlalchemy.Boolean,
                                                   default=False)