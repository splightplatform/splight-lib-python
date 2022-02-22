from django.test import TestCase

from splight_database.django.djatabase.models.namespace import Namespace, CrossNamespaceTryException
from splight_database.django.djatabase.models.connector import ClientConnector
from splight_database.django.djatabase.models.network import Network


class TestNamespace(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_create_namespace(self):
        namespace = Namespace.objects.create(id="123")
        self.assertIsInstance(namespace, Namespace)

    # TODO https://splight.atlassian.net/browse/FAC-223
    # def test_cross_tenant_try_m2m_raises(self):
    #     tenant = Tenant.objects.create(org_id="123")
    #     cross_tenant = Tenant.objects.create(org_id="345")
    #     tag = Tag.objects.create(type="name", value="TAG1", tenant=tenant)
    #     asset = Asset.objects.create(tenant=cross_tenant)
    #     asset.tags.add(tag)
    #     with self.assertRaises(CrossTenantTryException):
    #         asset.save()

    def test_cross_namespace_try_fk_raises(self):
        namespace = Namespace.objects.create()
        cross_namespace = Namespace.objects.create(id="123")
        net = Network.objects.create(name="NET1", namespace=namespace)
        with self.assertRaises(CrossNamespaceTryException):
            ClientConnector.objects.create(namespace=cross_namespace, network=net)
