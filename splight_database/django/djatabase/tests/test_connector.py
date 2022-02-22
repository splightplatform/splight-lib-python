from django.test import TestCase
from django.db.utils import IntegrityError
from parameterized import parameterized

from splight_database.django.djatabase.models.connector import Connector, ClientConnector, ServerConnector
from splight_database.django.djatabase.models.network import Network


class TestConnector(TestCase):
    def setUp(self) -> None:
        self.net = Network.objects.create(name="NET1")
        return super().setUp()

    def test_create_connector(self):
        conn = ClientConnector.objects.create(network=self.net, port=5001)
        self.assertIsInstance(conn, Connector)
        conn = ServerConnector.objects.create(network=self.net, port=1080, external_port=9999)
        self.assertIsInstance(conn, Connector)
    
    def test_server_connector_port_uniqueness(self):
        ServerConnector.objects.create(network=self.net, port=1080, external_port=9998)
        ServerConnector.objects.create(network=self.net, port=1080, external_port=9999)
        with self.assertRaises(IntegrityError):
            ServerConnector.objects.create(network=self.net, port=1080, external_port=9999)

    def test_create_multiple_clients(self):
        for _ in range(3):
            ClientConnector.objects.create(network=self.net, host="1.1.1.1", port=5001)
    
    def test_create_client_with_dns(self):
        ClientConnector.objects.create(network=self.net, host="this.hostname.com", port=5001)

    @parameterized.expand([
        ("A=2\nB=3", {'A': '2', 'B': '3'}),
        ("A=2B=3", {}),
        ("A=2\nB", {'A': '2'}),
        ("A=2\nB=3\r\nA=3", {'B': '3', 'A': '3'}),
    ])
    def test_extra_env(self, extra_properties, expected_env): 
        conn = ClientConnector.objects.create(network=self.net, host="this.hostname.com", port=5001, extra_properties=extra_properties)
        self.assertDictEqual(conn.extra_env, expected_env)