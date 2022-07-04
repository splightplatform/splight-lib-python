from django.test import TestCase
from splight_database.django.djatabase.models.namespace import Namespace, CrossNamespaceTryException
from splight_database.django.djatabase.models.asset import Asset, Attribute
from splight_database.django.djatabase.models.connector import Connector
from splight_database.django.djatabase.models.mapping import ClientMapping


class TestNamespace(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_create_namespace(self):
        namespace, _ = Namespace.objects.get_or_create(id="123")
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
        namespace, _ = Namespace.objects.get_or_create(id="123")
        cross_namespace, _ = Namespace.objects.get_or_create(id="1234")
        connector = Connector.objects.create(name="connector", version="dnp3", parameters=[], namespace=cross_namespace)
        attribute = Attribute.objects.create(name="attribute", namespace=namespace)
        asset = Asset.objects.create(name="asset", namespace=namespace)
        with self.assertRaises(CrossNamespaceTryException):
            ClientMapping.objects.create(asset=asset, attribute=attribute, connector=connector, path='pat', namespace=namespace)