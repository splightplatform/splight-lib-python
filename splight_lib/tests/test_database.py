from unittest import TestCase


class TestDatabase(TestCase):
    def test_import(self):
        from splight_models import Asset
        from splight_models import Attribute
        from splight_models import Trigger
        from splight_models import Network
        from splight_models import ClientConnector
        from splight_models import ServerConnector
        from splight_models import ClientMapping
        from splight_models import ServerMapping
        from splight_lib.database import DatabaseClient
