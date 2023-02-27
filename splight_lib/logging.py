import logging
import time
import os
import sys


def getLogger(name=None):
    return getComponentLogger(name)


def getComponentLogger(name="COMPONENT"):
    level = int(os.getenv('COMPONENT_LOG_LEVEL', logging.DEBUG))
    fmt = '%(levelname)s - %(name)s | %(asctime)s | %(filename)s:%(lineno)d | %(message)s'

    formatter = logging.Formatter(fmt=fmt)
    formatter.converter = time.gmtime

    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger


def getSplightDevLogger(name="SPLIGHT_DEV"):
    level = int(os.getenv('SPLIGHT_DEV_LOG_LEVEL', logging.DEBUG))
    fmt = '%(levelname)s - %(name)s | %(asctime)s | %(filename)s:%(lineno)d | %(message)s'

    formatter = logging.Formatter(fmt=fmt)
    formatter.converter = time.gmtime

    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
