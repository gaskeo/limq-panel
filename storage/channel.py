#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


import sqlalchemy
from .db_session import ModelBase

from .user import User


class Channel(ModelBase):
    __tablename__ = 'channels'

    name = sqlalchemy.Column(sqlalchemy.String(length=64), nullable=False)

    is_active = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)

    id = sqlalchemy.Column(sqlalchemy.String(length=16), nullable=False, primary_key=True, unique=True)

    owner_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey(User.id), nullable=False)


