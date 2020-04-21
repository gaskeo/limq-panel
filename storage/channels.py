#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


import sqlalchemy
from .db_session import ModelBase


class Channel(ModelBase):
    __tablename__ = 'channels'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    name = sqlalchemy.Column(sqlalchemy.String(length=64), nullable=False)

    is_active = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)

    public_id = sqlalchemy.Column(sqlalchemy.String(length=16), nullable=False)

    owner_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False)

    keys = sqlalchemy.Column(sqlalchemy.TEXT, nullable=True)

