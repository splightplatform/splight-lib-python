import logging
import time
import os


def getLogger(name=None):
    level = int(os.getenv('LOG_LEVEL', logging.DEBUG))
    log_file = os.getenv('LOG_FILE', None)
    fmt = '%(levelname)s | %(asctime)s | %(filename)s:%(lineno)d | %(message)s'
    config = {
        'level': level,
        'format': fmt,
    }
    if log_file:
        config['filename'] = log_file
        config['filemode'] = 'a'

    logging.basicConfig(**config)
    logging.Formatter.converter = time.gmtime

    return logging.getLogger(name)
