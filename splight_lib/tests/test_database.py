from unittest import TestCase


class TestDatabase(TestCase):
    def test_import(self):
        from splight_lib.database import Algorithm
        from splight_lib.database import Asset
        from splight_lib.database import Attribute
        from splight_lib.database import Trigger
        from splight_lib.database import Trigger
        from splight_lib.database import Network
        from splight_lib.database import ClientConnector
        from splight_lib.database import ServerConnector
        from splight_lib.database import ClientMapping
        from splight_lib.database import ServerMapping
        from splight_lib.database import DatabaseClient