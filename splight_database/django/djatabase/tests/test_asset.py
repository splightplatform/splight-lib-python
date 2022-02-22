from django.test import TestCase

from splight_database.django.djatabase.models.asset import Asset
from splight_database.django.djatabase.models.asset import Attribute, DuplicatedAttribute
from splight_database.django.djatabase.models.mapping import ValueMapping


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