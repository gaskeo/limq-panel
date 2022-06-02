#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


import sqlalchemy
import sqlalchemy.ext.declarative as dec
import sqlalchemy.orm as orm

from .url_creator import create_url

ModelBase = dec.declarative_base()

# Frontend Postgresql user (check init.sql)
url = create_url()
engine = sqlalchemy.create_engine(url, pool_size=20, pool_recycle=3600)


def base_init():
    # Base init
    ModelBase.metadata.create_all(engine)

    so = orm.sessionmaker(bind=engine)
    return so
