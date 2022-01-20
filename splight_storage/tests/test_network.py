from django.test import TestCase

from splight_storage.models.network import Network, upload_to
from splight_storage.models.tenant import Tenant


class TestNetwork(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_create_network(self):
        network = Network.objects.create(name="NET1")
        self.assertIsInstance(network, Network)

    def test_upload_to(self):
        tenant = Tenant.objects.create()
        network = Network.objects.create(name="NET1", tenant=tenant)
        destination = upload_to(network, "config.ovpn")
        org_id = tenant.org_id
        self.assertEqual(destination, f'Network/{org_id}/config.ovpn')