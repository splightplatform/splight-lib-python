from unittest import TestCase


class TestConnector(TestCase):
    def test_import_connector(self):
        from splight_lib.connector import ClientConnector, ServerConnector