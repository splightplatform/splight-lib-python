from django.test import TestCase
from splight_database.django.djatabase.models.network import Network


class TestNetwork(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_create_network(self):
        conn = Network.objects.create(name="Network", description="Description", version="A_VERSION", parameters=[{"key": "value"}])
        self.assertIsInstance(conn, Network)
