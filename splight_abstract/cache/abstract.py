import json
from functools import wraps
from typing import Callable, List
from abc import abstractmethod
from splight_abstract.client import AbstractClient
from splight_lib import logging


logger = logging.getLogger()


class AbstractCacheClient(AbstractClient):

    @abstractmethod
    def get(self, key):
        pass

    @abstractmethod
    def set(self, key, value):
        pass

    @abstractmethod
    def delete(self, key):
        pass

    @abstractmethod
    def clear(self):
        pass

# Decorators
def get_cache(client: AbstractCacheClient, cache_key: str, cache_key_args: str or List[str] = None) -> Callable:
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
                cached_data = client.get(final_cache_key)
            except Exception:
                logger.error(f'Error getting cache for {final_cache_key}')

            if isinstance(cached_data, bytes):
                logger.info(f'Cache hit for {final_cache_key}')

                return json.loads(cached_data.decode('utf-8'))
            else:
                cached_data = func(*args, **kwargs)

                try:
                    client.set(final_cache_key, json.dumps(cached_data), ex=3600)
                    logger.info(f'Cache update for {final_cache_key}')
                except Exception:
                    logger.error(f'Error getting cache for {final_cache_key}')

                return cached_data
        return wrapper
    return decorator


def flush_cache(client: AbstractCacheClient, cache_key: str, cache_key_args: str or List[str] = None, prefix_match=False) -> Callable:
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
                        final_cache_key += f':{key_arg}-{str(full_args.get(key_arg))}'

            try:
                if prefix_match:
                    final_cache_key += '*'
                client.delete(final_cache_key)
                logger.info(f'Cache flush for {final_cache_key}')
            except Exception:
                logger.error(f'Error flushing cache for {final_cache_key}')

            return func(*args, **kwargs)
        return wrapper
    return decorator
