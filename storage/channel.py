#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


from typing import Iterable

import sqlalchemy

from storage.keygen import CHAN_ID_LENGTH
from .db_session import ModelBase


class Channel(ModelBase):
    """
    SqlAlchemy-integrated channel descriptor.
    Has special methods for mixin management.
    """

    __tablename__ = 'channels'

    name = sqlalchemy.Column(sqlalchemy.String(length=64), nullable=False)
    id = sqlalchemy.Column(sqlalchemy.String(length=16), nullable=False, primary_key=True, unique=True)
    owner_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False)
    forwards = sqlalchemy.Column(sqlalchemy.String(length=512), nullable=True, unique=False)

    def mixins(self) -> Iterable:
        if self.forwards is None or len(self.forwards) == 0:
            return ()
        ll = len(self.forwards)

        return (self.forwards[i:i + CHAN_ID_LENGTH]
                for i in range(0, ll, CHAN_ID_LENGTH))

    def update_mixins(self, m: Iterable):
        srlzd = "".join(m)
        if not srlzd:
            srlzd = None
        self.forwards = srlzd
