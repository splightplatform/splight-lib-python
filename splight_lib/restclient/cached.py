"""
CacheObject definition for optimizations purposes.
"""


class CachedObject:
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if (cls, args, frozenset(kwargs.items())) not in cls._instances:
            instance = super().__new__(cls)
            instance.__init__(*args, **kwargs)
            cls._instances[(cls, args, frozenset(kwargs.items()))] = instance
        return cls._instances[(cls, args, frozenset(kwargs.items()))]
