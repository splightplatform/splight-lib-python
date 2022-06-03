from sqlite3 import connect
from django.test import TestCase
from splight_database.django.djatabase.models.asset import Asset, Attribute
from splight_database.django.djatabase.models.connector import Connector
from splight_database.django.djatabase.models.mapping import ClientMapping
from splight_database.django.djatabase.models.rule import MappingRule


class TestRule(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_create_client_mapping_rule(self):
        asset = Asset.objects.create()
        attr = Attribute.objects.create(name="attr")
        MappingRule.objects.create(asset=asset, attribute=attr, value="2", type="str", message="asd asd asd")
