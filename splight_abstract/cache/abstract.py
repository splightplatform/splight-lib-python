import json
from abc import abstractmethod
from functools import wraps
from typing import Callable, List

from splight_abstract.client import AbstractClient
from splight_lib.logging._internal import LogTags, get_splight_logger

logger = get_splight_logger()


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
def get_cache(
    client: AbstractCacheClient,
    cache_key: str,
    cache_key_args: str or List[str] = None,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Callable:
            final_cache_key = cache_key
            cached_data = None
            full_args = dict(zip(func.__code__.co_varnames, args))
            full_args.update(kwargs)
            if cache_key_args is not None:
                if isinstance(cache_key_args, str):
                    final_cache_key = f"{final_cache_key}:{cache_key_args}-{str(full_args.get(cache_key_args))}"
                else:
                    for key_arg in cache_key_args:
                        final_cache_key = f"{final_cache_key}:{key_arg}-{str(full_args.get(key_arg))}"

            try:
                cached_data = client.get(final_cache_key)
            except Exception:
                logger.error(
                    "Error getting cache for %s",
                    final_cache_key,
                    tags=LogTags.CACHE,
                )

            if isinstance(cached_data, bytes):
                logger.info(
                    "Cache hit for %s", final_cache_key, tags=LogTags.CACHE
                )

                return json.loads(cached_data.decode("utf-8"))
            else:
                cached_data = func(*args, **kwargs)

                try:
                    client.set(
                        final_cache_key, json.dumps(cached_data), ex=3600
                    )
                    logger.info(
                        "Cache update for %s",
                        final_cache_key,
                        tags=LogTags.CACHE,
                    )
                except Exception:
                    logger.error(
                        "Error getting cache for %s",
                        final_cache_key,
                        tags=LogTags.CACHE,
                    )

                return cached_data

        return wrapper

    return decorator


def flush_cache(
    client: AbstractCacheClient,
    cache_key: str,
    cache_key_args: str or List[str] = None,
    prefix_match=False,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Callable:
            final_cache_key = cache_key
            full_args = dict(zip(func.__code__.co_varnames, args))
            full_args.update(kwargs)
            if cache_key_args is not None:
                if isinstance(cache_key_args, str):
                    final_cache_key = f"{final_cache_key}:{cache_key_args}-{str(full_args.get(cache_key_args))}"
                else:
                    for key_arg in cache_key_args:
                        final_cache_key += (
                            f":{key_arg}-{str(full_args.get(key_arg))}"
                        )

            try:
                if prefix_match:
                    final_cache_key += "*"
                client.delete(final_cache_key)
                logger.info(
                    "Cache flush for %s", final_cache_key, tags=LogTags.CACHE
                )
            except Exception:
                logger.error(
                    "Error flushing cache for %s",
                    final_cache_key,
                    tags=LogTags.CACHE,
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator