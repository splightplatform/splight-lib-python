import logging
import time
import os
import sys
from typing import Dict


class SplightLogger:

    def __init__(self, name=None) -> None:
        # this is to avoid adding handlers to root logger
        # and interfering with third party app logs
        if name is None:
            name = "SplightLogger"
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)

        # hasHandlers returns True when self parent
        # have a handler so, don"t use method
        if not self.logger.handlers:
            self.load_handler()

    @property
    def log_level(self) -> int:
        return int(os.getenv("LOG_LEVEL", logging.DEBUG))

    @property
    def formatter(self) -> logging.Formatter:
        fmt = "%(levelname)s | %(asctime)s | %(filename)s:%(lineno)d | %(msg)s"
        formatter = logging.Formatter(fmt=fmt)
        formatter.converter = time.gmtime
        return formatter

    def load_handler(self) -> None:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(self.formatter)

        handler.setLevel(self.log_level)
        self.logger.addHandler(handler)
        self.logger.propagate = False

    @staticmethod
    def __format_msg(msg: str, tags: Dict) -> str:
        formatted_msg = msg
        if tags is not None:
            formatted_msg += " " + str([f"{k}:{v}" for k, v in tags.items()])
        return formatted_msg

    def debug(self, msg: str, tags: Dict=None, *args, **kwargs):
        formatted_msg = self.__format_msg(msg, tags)
        self.logger.debug(formatted_msg, *args, **kwargs)

    def info(self, msg: str, tags: Dict=None, *args, **kwargs):
        formatted_msg = self.__format_msg(msg, tags)
        self.logger.info(formatted_msg, *args, **kwargs)

    def warning(self, msg: str, tags: Dict=None, *args, **kwargs):
        formatted_msg = self.__format_msg(msg, tags)
        self.logger.warning(formatted_msg, *args, **kwargs)

    def error(self, msg: str, tags: Dict=None, *args, **kwargs):
        formatted_msg = self.__format_msg(msg, tags)
        self.logger.error(formatted_msg, *args, **kwargs)

    def exception(self, msg: str, tags: Dict=None, *args, **kwargs):
        formatted_msg = self.__format_msg(msg, tags)
        self.logger.exception(formatted_msg, *args, **kwargs)

    def critical(self, msg: str, tags: Dict=None, *args, **kwargs):
        formatted_msg = self.__format_msg(msg, tags)
        self.logger.critical(formatted_msg, *args, **kwargs)


class ComponentLogger(SplightLogger):

    def __init__(self, name=None) -> None:
        if name is None:
            name = "ComponentLogger"
        super().__init__(name)

    def load_handler(self) -> None:
        filename = os.getenv("LOG_FILE", "/tmp/components.log")
        handler = logging.FileHandler(filename=filename)
        handler.setFormatter(self.formatter)

        handler.setLevel(self.log_level)
        self.logger.addHandler(handler)
        self.logger.propagate = False


def getLogger(name=None):
    return ComponentLogger(name)


def getSplightLogger(name=None):
    return SplightLogger(name)
