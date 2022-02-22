from django.test import TestCase

from splight_database.django.djatabase.models.network import Network, upload_to
from splight_database.django.djatabase.models.namespace import Namespace


class TestNetwork(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_create_network(self):
        network = Network.objects.create(name="NET1")
        self.assertIsInstance(network, Network)

    def test_upload_to(self):
        namespace = Namespace.objects.create()
        network = Network.objects.create(name="NET1", namespace=namespace)
        destination = upload_to(network, "config.ovpn")
        namespace = namespace.id
        self.assertEqual(destination, f'Network/{namespace}/config.ovpn')
