from distutils.log import WARN
from logging import WARNING
from unittest import TestCase


class TestLogging(TestCase):
    def test_import_logging(self):
        from splight_lib import logging
        logger = logging.getLogger()
        logger.debug("DEBUG MESSAGE")
        logger.info("INFO MESSAGE")
        logger.warning("WARNING MESSAGE")
        logger.critical("CRITICAL MESSAGE")
        try:
            raise Exception("EXCEPTION MESSAGE")
        except Exception as e:
            logger.exception(e)

    def test_logger_message_present(self):
        from splight_lib import logging
        logger = logging.getLogger()
        message = "WARNING MESSAGE"
        with self.assertLogs() as captured:
            logger.warning(message)
        self.assertEqual(len(captured.records), 1)
        self.assertEqual(captured.records[0].getMessage(), message)
        self.assertEqual(captured.records[0].levelno, WARNING)
