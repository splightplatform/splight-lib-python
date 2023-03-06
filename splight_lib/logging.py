import logging
from logging.handlers import RotatingFileHandler
import time
import os
import sys
from typing import Dict


TAGS_KEY = "tags"


class SplightFormatter(logging.Formatter):
    DEFAULT_FMT: str = "%(levelname)s | %(asctime)s | %(filename)s:%(lineno)d | %(msg)s"

    def format(self, record):
        fmt = self.DEFAULT_FMT
        # add tags just if are present
        if record.tags is not None:
            fmt += " | %(tags)s"
        formatter = logging.Formatter(fmt=fmt)
        formatter.converter = time.gmtime
        return formatter.format(record)


class BaseSplightLogger:

    def __init__(self, name: str = None) -> None:
        # this is to avoid adding handlers to root logger
        # and interfering with third party app logs
        self.name = name if name is not None else "splight"
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.log_level)

        # hasHandlers returns True when self parent
        # have a handler so, don"t use method
        if not self.logger.handlers:
            self.load_handlers()

    def __repr__(self) -> str:
        level = logging.getLevelName(self.logger.getEffectiveLevel())
        return '<%s %s (%s)>' % (self.__class__.__name__, self.name, level)

    @property
    def log_level(self) -> int:
        return int(os.getenv("LOG_LEVEL", logging.DEBUG))

    @property
    def formatter(self) -> logging.Formatter:
        return SplightFormatter()

    def load_handlers(self) -> None:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(self.formatter)
        handler.setLevel(self.log_level)
        self.logger.addHandler(handler)
        self.logger.propagate = False

    def debug(self, msg: str, tags: Dict=None, *args, **kwargs):
        self.logger.debug(msg, extra={TAGS_KEY: tags}, *args, **kwargs)

    def info(self, msg: str, tags: Dict=None, *args, **kwargs):
        self.logger.info(msg, extra={TAGS_KEY: tags}, *args, **kwargs)

    def warning(self, msg: str, tags: Dict=None, *args, **kwargs):
        self.logger.warning(msg, extra={TAGS_KEY: tags}, *args, **kwargs)

    def error(self, msg: str, tags: Dict=None, *args, **kwargs):
        self.logger.error(msg, extra={TAGS_KEY: tags}, *args, **kwargs)

    def exception(self, msg: str, tags: Dict=None, *args, **kwargs):
        self.logger.exception(msg, extra={TAGS_KEY: tags}, *args, **kwargs)

    def critical(self, msg: str, tags: Dict=None, *args, **kwargs):
        self.logger.critical(msg, extra={TAGS_KEY: tags}, *args, **kwargs)


class SplightDevLogger(BaseSplightLogger):
    def __init__(self, name: str = None) -> None:
        name = name if name is not None else "splight-dev"
        super().__init__(name)

    def load_handlers(self) -> None:
        filename = os.getenv("SPLIGHT_DEVELOPER_LOG_FILE", "/tmp/splight-dev.log")
        max_bytes = int(os.getenv("SPLIGHT_DEVELOPER_MAX_BYTES", 5e+6))  # 5MB
        backup_count = int(os.getenv("SPLIGHT_DEVELOPER_BACKUP_COUNT", 100))
        handler = RotatingFileHandler(
            filename=filename, maxBytes=max_bytes, backupCount=backup_count
        )
        handler.setFormatter(self.formatter)
        handler.setLevel(self.log_level)

        self.logger.addHandler(handler)
        self.logger.propagate = False


class ComponentLogger(BaseSplightLogger):

    def __init__(self, name: str = None) -> None:
        name = name if name is not None else "component"
        super().__init__(name)

    def load_handlers(self) -> None:
        super().load_handlers()  # to load stdout handler
        # adding file handler
        filename = os.getenv("SPLIGHT_COMPONENT_LOG_FILE", "/tmp/components.log")
        max_bytes = int(os.getenv("SPLIGHT_COMPONENT_MAX_BYTES", 5e+6))  # 5MB
        backup_count = int(os.getenv("SPLIGHT_COMPONENT_BACKUP_COUNT", 100))
        handler = RotatingFileHandler(
            filename=filename, maxBytes=max_bytes, backupCount=backup_count
        )
        handler.setFormatter(self.formatter)

        handler.setLevel(self.log_level)
        self.logger.addHandler(handler)
        self.logger.propagate = False


def getLogger(name=None, dev=False):
    return SplightDevLogger(name) if dev else ComponentLogger(name)
