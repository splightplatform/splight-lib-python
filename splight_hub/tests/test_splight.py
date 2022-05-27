import json
from unittest import TestCase
from unittest.mock import patch
from parameterized import parameterized
from requests.models import Response
from splight_hub import SplightHubClient
from splight_models import Network, Algorithm, Connector, Rule


class TestVariable(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client = SplightHubClient(namespace="default", token="Splight abc def")

    def test_save_raises(self):
        with self.assertRaises(NotImplementedError):
            self.client.save(instance=None)

    def test_delete_raises(self):
        with self.assertRaises(NotImplementedError):
            self.client.delete(resource_type=None, id=1)

    def test_get_validate_resource_type(self):
        with self.assertRaises(NotImplementedError):
            self.client.get(resource_type=Rule)

    @parameterized.expand([
        (Network, []),
        (Network, [
            dict(id="123", name='Net1', description=None, version='01', parameters=[], readme_url=None, privacy_policy="private", tenant=None)
        ]),
        (Algorithm, []),
        (Algorithm, [
            dict(id="123", name='Algo1', description=None, version='01', parameters=[], readme_url=None, privacy_policy="private", tenant=None)
        ]),
        (Connector, []),
        (Connector, [
            dict(id="123", name='Conn1', description=None, version='01', parameters=[], readme_url=None, privacy_policy="private", tenant=None)
        ]),
    ])
    def test_get(self, class_, result):
        _response = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": result
        }
        response = Response()
        response.status_code = 200
        response._content = str.encode(json.dumps(_response))
        with patch("requests.get", return_value=response):
            response = self.client.get(resource_type=class_)
            self.assertEqual(response, result)