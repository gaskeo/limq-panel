#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\

from typing import List, Iterable, ClassVar

from redis import Redis
from queue import Queue

from storage.mixin import Mixin

REDIS_KEY_KEY = 'limq_isolate_{key}'
REDIS_MIXIN_KEY = 'limq_mixin_{channel_id}'


class RedisKeys:
    permissions = 'permissions'
    channel_id = 'channel_id'


class ChannelIdQueue(Queue):
    def __init__(self):
        super().__init__()

    def put_several(self, items: Iterable):
        for item in items:
            self.put(item)


def get_redis_key(key: str) -> str:
    return REDIS_KEY_KEY.format(key=key)


def get_redis_mixin(source_channel_id: str) -> str:
    return REDIS_MIXIN_KEY.format(channel_id=source_channel_id)


def set_key_permissions(sess: Redis, key: str, permissions: int):
    sess.hset(get_redis_key(key), RedisKeys.permissions,
              str(permissions))


def set_key_channel_id(sess: Redis, key: str, channel_id: str):
    sess.hset(REDIS_KEY_KEY.format(key=key), RedisKeys.channel_id,
              channel_id)


def delete_key(sess: Redis, key: str):
    sess.delete(REDIS_KEY_KEY.format(key=key))


def set_mixins(sess: Redis, src_channel_id: str, mixins: List[str]):
    sess.set(get_redis_mixin(src_channel_id), ','.join(mixins))


def get_mixins(sess: Redis, src_channel_id: str) -> List[str]:
    mixins = str(sess.get(get_redis_mixin(src_channel_id))) or ''
    return mixins.split(',') if mixins else []


def add_mixin(sess: Redis,
              src_channel_id: str, dest_channel_id: str):
    mixins = get_mixins(sess, src_channel_id)
    mixins.append(dest_channel_id)
    set_mixins(sess, src_channel_id, mixins)


def delete_mixin(sess: Redis, source_channel_id: str,
                 dest_channel_id: str):
    mixins = get_mixins(sess, source_channel_id)
    if dest_channel_id in mixins:
        mixins.remove(dest_channel_id)
        set_mixins(sess, source_channel_id, mixins)


def mixin_not_create_loop(db_sess: ClassVar, source_id: str,
                          dest_id: str
                          ) -> bool:
    def get_dest_ids(mixins: Iterable[Mixin]) -> List[str]:
        return [mixin.dest_channel for mixin in mixins]

    mixins_out_dest = db_sess.query(Mixin).filter(
        Mixin.source_channel == dest_id).all()

    if not mixins_out_dest:
        return True
    queue = ChannelIdQueue()
    queue.put_several(get_dest_ids(mixins_out_dest))

    while not queue.empty():
        next_id = queue.get()
        if next_id == source_id:
            return False

        mixins_out = db_sess.query(Mixin).filter(
            Mixin.source_channel == next_id).all()

        if mixins_out:
            queue.put_several(get_dest_ids(mixins_out))
    return True
