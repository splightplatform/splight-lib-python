import os
import sys
import time
from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    NOTSET,
    WARNING,
    Formatter,
    Handler,
    Logger,
    StreamHandler,
)
from logging import root as rootLogger
from typing import Dict, Optional

TAGS_KEY = "tags"


class SplightFormatter(Formatter):
    DEFAULT_FMT: str = (
        "%(levelname)s | %(asctime)s | %(filename)s:%(lineno)d | %(message)s"
    )

    def format(self, record):
        fmt = self.DEFAULT_FMT
        try:
            if record.tags is not None:
                fmt = " | ".join([fmt, "%(tags)s"])
        except AttributeError:
            pass  # tags aren't present
        formatter = Formatter(fmt=fmt)
        formatter.converter = time.gmtime
        return formatter.format(record)


class SplightLogger(Logger):
    def __init__(self, name: str = None) -> None:
        # this is to avoid adding handlers to root logger
        # and interfering with third party app logs
        self.name = name if name is not None else "splight"
        level = int(os.getenv("LOG_LEVEL", INFO))
        super().__init__(name, level)
        # the co_filename attribute is a property of the code object that
        # specifies the name of the file from which the code was compiled
        self._srcfile = os.path.normcase(
            standard_output_handler.__code__.co_filename
        )

    @property
    def formatter(self) -> Formatter:
        return SplightFormatter()

    @staticmethod
    def _update_kwargs(kwargs: Dict) -> Dict:
        """Format log method tags and save into `extra` logging argument."""
        tags = kwargs.pop(TAGS_KEY, None)
        if tags is not None:
            kwargs.update({"extra": {TAGS_KEY: tags}})
        return kwargs

    def _log(
        self,
        level,
        msg,
        args,
        exc_info=None,
        extra=None,
        stack_info=False,
        stacklevel=1,
    ):
        """
        This is a copy from logging._log, where it only changes the `_srcfile`
        variable to use `self._scrfile` because we need to update it for current
        file, i.e, splight_lib.logging.py to show the correct log caller file in
        formatter.
        """
        sinfo = None
        if self._srcfile:
            # IronPython doesn't track Python frames, so findCaller raises an
            # exception on some versions of IronPython. We trap it here so that
            # IronPython can use logging.
            try:
                fn, lno, func, sinfo = self.findCaller(stack_info, stacklevel)
            except ValueError:  # pragma: no cover
                fn, lno, func = "(unknown file)", 0, "(unknown function)"
        else:  # pragma: no cover
            fn, lno, func = "(unknown file)", 0, "(unknown function)"
        if exc_info:
            if isinstance(exc_info, BaseException):
                exc_info = (type(exc_info), exc_info, exc_info.__traceback__)
            elif not isinstance(exc_info, tuple):
                exc_info = sys.exc_info()
        record = self.makeRecord(
            self.name, level, fn, lno, msg, args, exc_info, func, extra, sinfo
        )
        self.handle(record)

    def setLevel(self, level, update_handlers=True):
        super().setLevel(level)
        if update_handlers:
            for h in self.handlers:
                h.setLevel(level)
        # Add logger.level to root logger
        rootLogger.setLevel(level)

    def debug(self, msg: str, *args, **kwargs):
        if self.isEnabledFor(DEBUG):
            kwargs = self._update_kwargs(kwargs)
            self._log(DEBUG, msg, args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        if self.isEnabledFor(INFO):
            kwargs = self._update_kwargs(kwargs)
            self._log(INFO, msg, args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        if self.isEnabledFor(WARNING):
            kwargs = self._update_kwargs(kwargs)
            self._log(WARNING, msg, args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        if self.isEnabledFor(ERROR):
            kwargs = self._update_kwargs(kwargs)
            self._log(ERROR, msg, args, **kwargs)

    def exception(self, msg: str, *args, exc_info=True, **kwargs):
        if self.isEnabledFor(ERROR):
            kwargs = self._update_kwargs(kwargs)
            self._log(ERROR, msg, args, exc_info=exc_info, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        if self.isEnabledFor(CRITICAL):
            kwargs = self._update_kwargs(kwargs)
            self._log(CRITICAL, msg, args, **kwargs)


def standard_output_handler(
    formatter: Optional[Formatter] = SplightFormatter(),
    log_level: Optional[str] = INFO,
) -> Handler:
    handler = StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(log_level)
    return handler
