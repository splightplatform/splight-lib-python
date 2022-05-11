from typing import Dict, Optional
from splight_cache.abstract import AbstractCacheClient


class FakeCacheClient(AbstractCacheClient):

    data: Dict[str, str] = dict()

    def __init__(self, *args, **kwargs):
        super(FakeCacheClient, self).__init__(*args, **kwargs)

    def get(self, key) -> Optional[bytes]:
        val = self.data.get(key, None)
        return val.encode("utf-8") if val else None

    def set(self, key, value, *args, **kwargs):
        self.data[key] = value

    def delete(self, key):
        del self.data[key]

    def clear(self):
        self.data.clear()
