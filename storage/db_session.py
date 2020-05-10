#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


import sqlalchemy
import sqlalchemy.ext.declarative as dec
import sqlalchemy.orm as orm

ModelBase = dec.declarative_base()

# Frontend MySQL user (check init.sql)
engine = sqlalchemy.create_engine("mysql://limq-front:i77dj9wobb@localhost/limq?charset=utf8mb4")


def base_init():
    # Base init
    ModelBase.metadata.create_all(engine)

    so = orm.sessionmaker(bind=engine)
    return so

