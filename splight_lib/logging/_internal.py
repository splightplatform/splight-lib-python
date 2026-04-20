import os
from enum import auto
from logging import INFO, Formatter, Handler
from typing import Optional

from concurrent_log_handler import ConcurrentRotatingFileHandler
from strenum import UppercaseStrEnum

from splight_lib.logging.logging import (
    SplightFormatter,
    SplightLogger,
    standard_output_handler,
)


class LogTags(UppercaseStrEnum):
    RUNTIME = auto()
    INDEX = auto()
    SECRET = auto()
    HOOK = auto()
    SETPOINT = auto()
    PARAMETER = auto()
    COMPONENT = auto()
    DATABASE = auto()
    DATALAKE = auto()
    CACHE = auto()


# don't used now
def splight_dev_file_handler(
    formatter: Optional[Formatter] = SplightFormatter(),
    log_level: Optional[str] = INFO,
) -> Handler:
    filename = os.getenv("SPLIGHT_DEVELOPER_LOG_FILE", "/tmp/splight-dev.log")
    max_bytes = int(os.getenv("SPLIGHT_DEVELOPER_MAX_BYTES", 5e6))  # 5MB
    backup_count = int(os.getenv("SPLIGHT_DEVELOPER_BACKUP_COUNT", 100))

    handler = ConcurrentRotatingFileHandler(
        filename=filename, maxBytes=max_bytes, backupCount=backup_count
    )
    handler.setFormatter(formatter)
    handler.setLevel(log_level)
    return handler


def get_splight_logger(name: Optional[str] = None):
    """Stdout logger."""
    if name is None:
        name = "splight-dev"
    logger = SplightLogger(name=name)
    logger.propagate = False
    stdout_handler = standard_output_handler(log_level=logger.level)
    logger.addHandler(stdout_handler)
    logger.setLevel(logger.level)
    return logger
