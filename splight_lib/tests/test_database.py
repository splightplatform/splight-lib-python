from unittest import TestCase


class TestDatabase(TestCase):
    def test_import(self):
        from splight_abstract.database import AbstractDatabaseClient