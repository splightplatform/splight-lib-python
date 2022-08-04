from unittest import TestCase


class TestDatalake(TestCase):
    def test_import_datalake(self):
        from splight_abstract.datalake import AbstractDatalakeClient