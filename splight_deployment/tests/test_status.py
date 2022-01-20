from unittest import TestCase
import json
from splight_deployment.status import Status


class TestStatus(TestCase):
    def test_status_json(self):
        status_dict = {
            "id": 1,
            "deployment_name": "dpmt_1",
            "status": "running",
            "detail": "This is a sample detail text"
        }
        status = Status(**status_dict)
        self.assertIsInstance(status.json(), str)
        self.assertEqual(status.json(), json.dumps(status_dict))

    def test_status_dict(self):
        status_dict = {
            "id": 1,
            "deployment_name": "dpmt_1",
            "status": "running",
            "detail": "This is a sample detail text"
        }
        status = Status(**status_dict)
        self.assertIsInstance(status.dict(), dict)
        self.assertDictEqual(status.dict(), status_dict)
