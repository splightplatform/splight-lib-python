from distutils.log import WARN
from logging import WARNING
from unittest import TestCase
from splight_lib.logging import getLogger
import pytest


class TestLogging(TestCase):

    def test_get_logger_different(self):
        assert getLogger(dev=True).logger.name != getLogger().logger.name

    def test_log_formatter_and_tags(logger):
        for logger in (getLogger(dev=True), getLogger()):
            logger.debug("%s", "Hello World", tags="context")
            logger.info("%s", "Hello World", tags=["context"])
            logger.warning("%s", "Hello World", tags={"context": "CONTEXT"})
            logger.critical("%s", "Hello World", tags="context")
            try:
                raise Exception("Some error.")
            except Exception as e:
                logger.exception("%s", e, tags="context")

    def test_logger_message_present(self):
        from splight_lib import logging
        logger = logging.BaseSplightLogger()
        message = "WARNING MESSAGE"
        with self.assertLogs(logger=logger.name, level=logger.log_level) as captured:
            logger.warning(message)
        self.assertEqual(len(captured.records), 1)
        self.assertEqual(captured.records[0].getMessage(), message)
        self.assertEqual(captured.records[0].levelno, WARNING)
