import logging
import os


def getLogger(name=None):
    level = logging.DEBUG if os.getenv('DEBUG', False) else logging.INFO
    logging.basicConfig(format='%(levelname)s | Date-Time : %(asctime)s | File: %(filename)s | Function: %(funcname)s | Line No. : %(lineno)d - %(message)s', level=level)
    return logging.getLogger(name)
