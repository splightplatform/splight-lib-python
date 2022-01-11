from django.test import TestCase
from splight_lib.asset import Asset, Attribute, Bus
# from splight_lib.electrical.asset import Bus
from splight_lib.mapping import ValueMapping, ReferenceMapping
from splight_lib.mapping import CyclicReference, InvalidReference


class TestMapping(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_value_mapping(self):
        # Create Generic asset
        scada1 = Asset.objects.create()
        with self.assertRaises(AttributeError):
            scada1.get("p")
        p = Attribute.objects.create(name="p")
        mapping1 = ValueMapping.objects.create(asset=scada1, attribute=p, value="5")
        self.assertEqual(scada1.get("p"), mapping1.value, "5")

    def test_reference_mapping(self):
        scada1 = Asset.objects.create()
        p = Attribute.objects.create(name="p")
        v = ValueMapping.objects.create(asset=scada1, attribute=p, value="5")

        bus1 = Asset.objects.create()
        ReferenceMapping.objects.create(asset=bus1, attribute=p, ref_asset=scada1, ref_attribute=p)

        self.assertEqual(bus1.get("p"), scada1.get("p"), "5")

    def test_cyclic_reference_raises(self):
        # Create Generic asset
        scada1 = Asset.objects.create()
        p = Attribute.objects.create(name="p")

        ValueMapping(scada1, p, value="5")
        # Create typed asset with predefined attributes
        bus1 = Bus.objects.create()
        # Add ReferenceMapping
        base_voltage = Attribute.objects.create(name="base_voltage")
        ReferenceMapping.objects.create(asset=bus1, attribute=base_voltage, ref_asset=scada1, ref_attribute=p)

        with self.assertRaises(CyclicReference):
            ReferenceMapping.objects.create(asset=scada1, attribute=p, ref_asset=bus1, ref_attribute=base_voltage)

    def test_set_value_mapping(self):
        scada1 = Asset.objects.create()
        p = Attribute.objects.create(name="p")
        ValueMapping.objects.create(asset=scada1, attribute=p, value="5")
        scada1.set("p", "10")
        self.assertEqual(scada1.get("p"), "10")

    def test_set_reference_mapping(self):
        scada1 = Asset.objects.create()
        p = Attribute.objects.create(name="p")
        ValueMapping.objects.create(asset=scada1, attribute=p, value="5")
        base_voltage = Attribute.objects.create(name="base_voltage")
        bus1 = Asset.objects.create()
        ReferenceMapping.objects.create(asset=bus1, attribute=base_voltage, ref_asset=scada1, ref_attribute=p)
        bus1.set("base_voltage", "10")
        self.assertEqual(bus1.get("base_voltage"), scada1.get("p"), "10")

    def test_set_attribute_not_exist(self):
        scada1 = Asset.objects.create()
        with self.assertRaises(AttributeError):
            scada1.set("p", "10")

    def test_set_asset_has_not_attribute(self):
        scada1 = Asset.objects.create()
        Attribute.objects.create(name="p")
        with self.assertRaises(AttributeError):
            scada1.set("p", "10")

    # def test_invalid_reference_mapping_raises(self):
    #     # Create Generic asset
    #     scada1 = Asset.objects.create()
    #     p = Attribute.objects.create(name="p")
    #     # Create typed asset with predefined attributes
    #     bus1 = Bus.objects.create()
    #     # Add ReferenceMapping
    #     base_voltage = Attribute.objects.create(name="base_voltage")
    #     with self.assertRaises(InvalidReference):
    #         ReferenceMapping.objects.create(asset=bus1, attribute=base_voltage, ref_asset=scada1, ref_attribute=p)
