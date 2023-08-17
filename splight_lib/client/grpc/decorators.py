from time import sleep
from typing import Callable

import grpc

from splight_lib.logging._internal import get_splight_logger

logger = get_splight_logger()


class GRPCRetryError(Exception):
    pass


def retry_streaming(
    times: int = 3, delay: float = 0.5, delay_factor: float = 2
):
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except grpc.RpcError as e:
                logger.error(f"Error: {e}")
                if times == 0:
                    raise GRPCRetryError("Max retries exceeded")
                sleep(delay)
                logger.warn(f"Retrying {func.__name__}, {times} retries left")
                retry_streaming(times - 1, delay * delay_factor)(func)(
                    *args, **kwargs
                )

        return wrapper

    return decorator
