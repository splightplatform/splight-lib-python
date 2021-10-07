import unittest
from fake_splight_lib.connector import FakeConnector
from fake_splight_lib.component import FakeComponent
from splight_lib.component import DOComponentInterface
from splight_lib.asset import RelayAsset


class TestComponent(unittest.TestCase):
    def test_component_creation(self):
        component = FakeComponent()
        asset = RelayAsset(name='JustADummyRelay', connector=FakeConnector())
        self.assertIsInstance(component, DOComponentInterface)
        self.assertTrue(component.is_applicable(asset))
