import os
from typing import Optional
from logging import Formatter, Handler, INFO, basicConfig
from .logging import SplightFormatter, SplightLogger, standard_output_handler
from concurrent_log_handler import ConcurrentRotatingFileHandler


def component_file_handler(
    formatter: Optional[Formatter] = SplightFormatter(),
    log_level: Optional[str] = INFO
) -> Handler:
    filename = os.getenv("SPLIGHT_COMPONENT_LOG_FILE", "/tmp/components.log")
    max_bytes = int(os.getenv("SPLIGHT_COMPONENT_MAX_BYTES", 5e+6))  # 5MB
    backup_count = int(os.getenv("SPLIGHT_COMPONENT_BACKUP_COUNT", 100))

    handler = ConcurrentRotatingFileHandler(
        filename=filename, maxBytes=max_bytes, backupCount=backup_count
    )
    handler.setFormatter(formatter)
    handler.setLevel(log_level)
    return handler


def get_component_logger(name: Optional[str] = None):
    """Stdout and file logger."""
    if name is None:
        name = "component"
    logger = SplightLogger(name=name)
    logger.propagate = False
    stdout_handler = standard_output_handler(log_level=logger.level)
    logger.addHandler(stdout_handler)
    file_handler = component_file_handler(log_level=logger.level)
    logger.addHandler(file_handler)

    # Add logger.level to root logger
    logger.setLevel(logger.level)
    return logger


def getLogger(name: Optional[str] = None):
    return get_component_logger(name)
