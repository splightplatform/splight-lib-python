from django.test import TestCase

from splight_storage.models.asset import Asset
from splight_storage.models.asset.attribute import Attribute, DuplicatedAttribute
from splight_storage.models.mapping import ValueMapping


class TestAttribute(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_create_attribute(self):
        Attribute.objects.create(name="attr")

    def test_duplicated_attribute_raises(self):
        Attribute.objects.create(name="attr")
        with self.assertRaises(DuplicatedAttribute):
            Attribute.objects.create(name="attr")


class TestAsset(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_create_asset(self):
        Asset.objects.create()

    def test_set_then_get(self):
        asset = Asset.objects.create()
        q = Attribute.objects.create(name="q")
        val = ValueMapping.objects.create(asset=asset, attribute=q, value=5)
        asset.set("q", 10)
        val.refresh_from_db()
        self.assertEqual(asset.get("q"), "10")

    def test_get_default_on_missing_attr(self):
        scada1 = Asset.objects.create()
        with self.assertRaises(AttributeError):
            scada1.get("missing_attr")
        self.assertEqual(scada1.get("missing_attr", 10), 10)
    
    def test_get_default_on_present_attr(self):
        scada1 = Asset.objects.create()
        present_attr = Attribute.objects.create(name="present_attr")
        ValueMapping.objects.create(asset=scada1, attribute=present_attr, value=5)
        self.assertEqual(scada1.get("present_attr", 10), scada1.get("present_attr"), 5)
