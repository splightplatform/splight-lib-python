from django.test import TestCase
from splight_storage.models.asset import Asset, Attribute, Bus
from splight_storage.models.mapping import ClientMapping
from splight_storage.models.mapping import ValueMapping, ReferenceMapping
from splight_storage.models.mapping import CyclicReference
from splight_lib.communication import ExternalCommunicationClient
from splight_lib.communication import Message


class TestMapping(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_value_mapping_get(self):
        # Create Generic asset
        scada1 = Asset.objects.create()
        with self.assertRaises(AttributeError):
            scada1.get("q")
        q = Attribute.objects.create(name="q")
        mapping1 = ValueMapping.objects.create(asset=scada1, attribute=q, value="5")
        self.assertEqual(scada1.get("q"), mapping1.value, "5")

    def test_reference_mapping_get(self):
        scada1 = Asset.objects.create()
        q = Attribute.objects.create(name="q")
        v = ValueMapping.objects.create(asset=scada1, attribute=q, value="5")

        bus1 = Asset.objects.create()
        ReferenceMapping.objects.create(asset=bus1, attribute=q, ref_asset=scada1, ref_attribute=q)

        self.assertEqual(bus1.get("q"), scada1.get("q"), "5")

    def test_client_mapping_get(self):
        scada1 = Asset.objects.create()
        p = Attribute.objects.create(name="p")
        c = ClientMapping.objects.create(asset=scada1, attribute=p)
        self.assertEqual(scada1.get("p"), 5)

    def test_client_mapping_get_raises(self):
        scada1 = Asset.objects.create()
        p = Attribute.objects.create(name="p")
        c = ClientMapping.objects.create(asset=scada1, attribute=p)

        with self.assertRaises(AttributeError):
            scada1.get("q")

    def test_client_mapping_set(self):
        scada1 = Asset.objects.create()
        p = Attribute.objects.create(name="p")
        ClientMapping.objects.create(asset=scada1, attribute=p)
        scada1.set("p", "10")
        queue = ExternalCommunicationClient()
        data = queue.receive()
        msg = Message(**data)
        self.assertEqual(msg.variables[0].field, "p")
        self.assertEqual(msg.variables[0].args, {"value": "10"})

    def test_reference_mapping_set(self):
        scada1 = Asset.objects.create()
        p = Attribute.objects.create(name="p")
        ClientMapping.objects.create(asset=scada1, attribute=p)
        base_voltage = Attribute.objects.create(name="base_voltage")
        bus1 = Asset.objects.create()
        ReferenceMapping.objects.create(asset=bus1, attribute=base_voltage, ref_asset=scada1, ref_attribute=p)
        bus1.set("base_voltage", "10")
        queue = ExternalCommunicationClient()
        data = queue.receive()
        msg = Message(**data)
        self.assertEqual(msg.variables[0].field, "p")
        self.assertEqual(msg.variables[0].args, {"value": "10"})

    def test_unexistent_attribute_set_raises(self):
        scada1 = Asset.objects.create()
        with self.assertRaises(AttributeError):
            scada1.set("p", "10")

    def test_attribute_without_mapping_set_raises(self):
        scada1 = Asset.objects.create()
        Attribute.objects.create(name="p")
        with self.assertRaises(AttributeError):
            scada1.set("p", "10")

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
