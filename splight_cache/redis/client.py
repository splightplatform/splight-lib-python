from redis import Redis

from splight_lib import logging
from splight_cache.abstract import AbstractCacheClient
from .settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

logger = logging.getLogger()


class RedisClient(AbstractCacheClient):

    def __init__(self, *args, **kwargs):
        self.redis = Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=0)
        super(RedisClient, self).__init__(*args, **kwargs)

    def get(self, key) -> bytes:
        val = self.redis.get(key)
        return val

    def set(self, key, value, *args, **kwargs):
        self.redis.set(key, value, *args, **kwargs)

    def delete(self, key):
        self.redis.delete(key)

    def clear(self):
        self.redis.flushdb()
