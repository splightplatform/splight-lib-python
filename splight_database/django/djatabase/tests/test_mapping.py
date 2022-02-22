from django.test import TestCase
from splight_database.django.djatabase.models.asset import Asset, Attribute
from splight_database.django.djatabase.models.mapping import ClientMapping
from splight_database.django.djatabase.models.mapping import ValueMapping, ReferenceMapping
from splight_database.django.djatabase.models.mapping import CyclicReference


class TestMapping(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_value_mapping_get(self):
        # Create Generic asset
        scada1 = Asset.objects.create()
        q = Attribute.objects.create(name="q")
        mapping1 = ValueMapping.objects.create(asset=scada1, attribute=q, value="5")
        self.assertEqual(mapping1.value, "5")

    def test_reference_mapping_get(self):
        scada1 = Asset.objects.create()
        q = Attribute.objects.create(name="q")
        v = ValueMapping.objects.create(asset=scada1, attribute=q, value="5")

        bus1 = Asset.objects.create()
        ReferenceMapping.objects.create(asset=bus1, attribute=q, ref_asset=scada1, ref_attribute=q)
        self.assertEqual(v.value, "5")

    def test_client_mapping_get(self):
        scada1 = Asset.objects.create()
        p = Attribute.objects.create(name="p")
        ClientMapping.objects.create(asset=scada1, attribute=p)

    def test_cyclic_reference_raises(self):
        # Create Generic asset
        scada1 = Asset.objects.create()
        bus1 = Asset.objects.create()
        p = Attribute.objects.create(name="p")
        base_voltage = Attribute.objects.create(name="base_voltage")

        # Add ReferenceMapping
        ReferenceMapping.objects.create(asset=bus1, attribute=base_voltage, ref_asset=scada1, ref_attribute=p)
        with self.assertRaises(CyclicReference):
            ReferenceMapping.objects.create(asset=scada1, attribute=p, ref_asset=bus1, ref_attribute=base_voltage)
