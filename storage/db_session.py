#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


import sqlalchemy
import sqlalchemy.orm as orm
import sqlalchemy.ext.declarative as dec


ModelBase = dec.declarative_base()


engine = sqlalchemy.create_engine("mysql://limq-front:i77dj9wobb@localhost/limq")


def base_init():
    ModelBase.metadata.create_all(engine)

    so = orm.sessionmaker(bind=engine)
    return so

