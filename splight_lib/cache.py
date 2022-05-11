import os
import json
import ast

from functools import wraps
from typing import Callable, List

from splight_lib import logging
from splight_cache.redis import RedisClient
from fake_splight_lib.cache import FakeCacheClient

logger = logging.getLogger()

if ast.literal_eval(os.getenv("FAKE_CACHE", "True")):
    CacheClient = FakeCacheClient()
else:
    CacheClient = RedisClient()


def get_cache(cache_key: str, cache_key_args: str or List[str] = None) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Callable:
            final_cache_key = cache_key
            cached_data = None
            full_args = dict(zip(func.__code__.co_varnames, args))
            full_args.update(kwargs)
            if cache_key_args is not None:
                if isinstance(cache_key_args, str):
                    final_cache_key = f'{final_cache_key}:{cache_key_args}-{str(full_args.get(cache_key_args))}'
                else:
                    for key_arg in cache_key_args:
                        final_cache_key = f'{final_cache_key}:{key_arg}-{str(full_args.get(key_arg))}'

            try:
                cached_data = CacheClient.get(final_cache_key)
            except Exception:
                logger.error(f'Error getting cache for {final_cache_key}')

            if isinstance(cached_data, bytes):
                logger.info(f'Cache hit for {final_cache_key}')

                return json.loads(cached_data.decode('utf-8'))
            else:
                cached_data = func(*args, **kwargs)

                try:
                    CacheClient.set(final_cache_key, json.dumps(cached_data), ex=3600)
                    logger.info(f'Cache update for {final_cache_key}')
                except Exception:
                    logger.error(f'Error getting cache for {final_cache_key}')

                return cached_data
        return wrapper
    return decorator


def flush_cache(cache_key: str, cache_key_args: str or List[str] = None) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Callable:
            final_cache_key = cache_key
            full_args = dict(zip(func.__code__.co_varnames, args))
            full_args.update(kwargs)
            if cache_key_args is not None:
                if isinstance(cache_key_args, str):
                    final_cache_key = f'{final_cache_key}:{cache_key_args}-{str(full_args.get(cache_key_args))}'
                else:
                    for key_arg in cache_key_args:
                        final_cache_key = f'{final_cache_key}:{key_arg}-{str(full_args.get(key_arg))}'

            try:
                CacheClient.delete(final_cache_key)
                logger.info(f'Cache flush for {final_cache_key}')
            except Exception:
                logger.error(f'Error flushing cache for {final_cache_key}')

            return func(*args, **kwargs)
        return wrapper
    return decorator


def clear_cache():
    logger.info(f'Clearing cache')
    CacheClient.clear()
