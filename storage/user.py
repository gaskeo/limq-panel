#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\

import sqlalchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, \
    check_password_hash

from .db_session import ModelBase
from .keygen import generate_salt


class User(ModelBase, UserMixin):
    """
    SqlAlchemy-integrated user descriptor.
    """

    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.String(length=32),
                           primary_key=True)

    username = sqlalchemy.Column(sqlalchemy.String(length=32),
                                 nullable=True)

    email = sqlalchemy.Column(sqlalchemy.String(length=64),
                              nullable=True,
                              unique=True)

    hashed_password = sqlalchemy.Column(sqlalchemy.String(length=128),
                                        nullable=True)

    salt = sqlalchemy.Column(sqlalchemy.String(length=8), nullable=True)

    def set_password(self, password):
        salt = generate_salt()
        self.salt = salt
        self.hashed_password = generate_password_hash(password + salt)

    def check_password(self, password):
        return check_password_hash(self.hashed_password,
                                   password + self.salt)
