#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


import sqlalchemy

from .channel import Channel
from .db_session import ModelBase


class Mixin(ModelBase):
    """
    SqlAlchemy-integrated access key descriptor.
    """

    __tablename__ = "mixins"

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True,
                           autoincrement=True)

    source_channel = sqlalchemy.Column(sqlalchemy.String(length=16),
                                       nullable=False)

    dest_channel = sqlalchemy.Column(sqlalchemy.String(length=16),
                                     nullable=False)

    linked_by = sqlalchemy.Column(sqlalchemy.String(length=32),
                                  nullable=False)
