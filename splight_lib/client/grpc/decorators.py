from time import sleep
from typing import Callable

import grpc
from splight_lib.logging._internal import get_splight_logger

logger = get_splight_logger()


def retry_streaming(times=3, delay=0.5, delay_factor=2):
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except grpc.RpcError as e:
                print(f"Error: {e}")
                logger.error(f"Error: {e}")
                sleep(1)
                if times == 0:
                    raise grpc.RpcError("Max retries exceeded")
                sleep(delay)
                logger.debug(f"Retrying {func.__name__}, {times} retries left")
                retry_streaming(times - 1, delay * delay_factor)(func)(
                    *args, **kwargs
                )

        return wrapper

    return decorator
