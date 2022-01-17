import logging
import os


def getLogger(name=None):
    level = os.getenv('LOGLEVEL', logging.DEBUG)
    fmt = '%(levelname)s | %(asctime)s | %(filename)s:%(lineno)d | %(message)s'
    logging.basicConfig(format=fmt, level=level)
    return logging.getLogger(name)
