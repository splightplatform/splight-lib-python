import unittest
from splight_lib.devices import Device
from splight_lib.status import STATUS_OK


class TestDevice(unittest.TestCase):

    def test_device_creation(self):
        device = Device()
        self.assertIsInstance(device, Device)

    def test_device_status_property(self):
        device = Device()
        self.assertEqual(device.status, STATUS_OK)


if __name__ == '__main__':
    unittest.main()