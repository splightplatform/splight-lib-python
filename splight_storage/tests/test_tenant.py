from django.test import TestCase

from splight_storage.models.tenant import Tenant, CrossTenantTryException
from splight_storage.models.tag import Tag
from splight_storage.models.asset import Asset
from splight_storage.models.connector import ClientConnector
from splight_storage.models.network import Network


class TestTenant(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_create_tenant(self):
        tenant = Tenant.objects.create(org_id="123")
        self.assertIsInstance(tenant, Tenant)

    # TODO https://splight.atlassian.net/browse/FAC-223
    # def test_cross_tenant_try_m2m_raises(self):
    #     tenant = Tenant.objects.create(org_id="123")
    #     cross_tenant = Tenant.objects.create(org_id="345")
    #     tag = Tag.objects.create(type="name", value="TAG1", tenant=tenant)
    #     asset = Asset.objects.create(tenant=cross_tenant)
    #     asset.tags.add(tag)
    #     with self.assertRaises(CrossTenantTryException):
    #         asset.save()

    def test_cross_tenant_try_fk_raises(self):
        tenant = Tenant.objects.create(org_id="123")
        cross_tenant = Tenant.objects.create(org_id="345")
        net = Network.objects.create(name="NET1", tenant=tenant)
        with self.assertRaises(CrossTenantTryException):
            ClientConnector.objects.create(tenant=cross_tenant, network=net)
