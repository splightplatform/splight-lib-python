from django.test import TestCase
from splight_database.django.djatabase.models.connector import Connector


class TestConnector(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_create_connector(self):
        conn = Connector.objects.create(name="Connector", description="Description", version="A_VERSION", parameters=[{"key": "value"}])
        self.assertIsInstance(conn, Connector)
