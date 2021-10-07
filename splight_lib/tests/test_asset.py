import unittest
from splight_lib.asset import Asset, Network, RelayAsset
from fake_splight_lib.connector import FakeConnector
from splight_lib.status import STATUS_UNKNOWN


class TestAsset(unittest.TestCase):

    def test_asset_creation(self):
        asset = RelayAsset(name='JustADummyRelay', connector=FakeConnector())
        self.assertIsInstance(asset, Asset)
        self.assertIsInstance(asset, RelayAsset)

    def test_asset_status_property(self):
        asset = RelayAsset(name='JustADummyRelay', connector=FakeConnector())
        self.assertEqual(asset.status, STATUS_UNKNOWN)

class TestNetwork(unittest.TestCase):

    def test_network_creation(self):
        asset = RelayAsset(name='JustADummyRelay', connector=FakeConnector())
        asset2 = RelayAsset(name='JustAnotherDummyRelay', connector=FakeConnector())
        net = Network(name='JustANetwork')
        self.assertIsInstance(net, Network)
        self.assertEqual(len(net.get_assets()), 0)
        net.add_asset(asset)
        self.assertEqual(len(net.get_assets()), 1)
        net.add_asset(asset2)
        self.assertIn(asset, net.get_assets())
        self.assertIn(asset2, net.get_assets())


if __name__ == '__main__':
    unittest.main()