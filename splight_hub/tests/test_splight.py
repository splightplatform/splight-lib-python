import json
from unittest import TestCase
from unittest.mock import patch
from parameterized import parameterized
from requests.models import Response
from splight_hub import SplightHubClient
from splight_models import HubNetwork, HubAlgorithm, HubConnector, MappingRule


class TestVariable(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client = SplightHubClient(namespace="default", token="Bearer abcdef")

    def test_save_raises(self):
        with self.assertRaises(NotImplementedError):
            self.client.save(instance=None)

    def test_delete_raises(self):
        with self.assertRaises(NotImplementedError):
            self.client.delete(resource_type=None, id=1)

    def test_get_validate_resource_type(self):
        with self.assertRaises(NotImplementedError):
            self.client.get(resource_type=MappingRule, first=True)

    @parameterized.expand([
        (HubNetwork, []),
        (HubNetwork, [
            dict(id="123", name='Net1', description=None, version='01', impact=1, parameters=[], readme_url=None, privacy_policy="private", tenant=None, picture_url=None, verification=None, last_modified=None)
        ]),
        (HubAlgorithm, []),
        (HubAlgorithm, [
            dict(id="123", name='Algo1', description=None, version='01', impact=1, parameters=[], readme_url=None, privacy_policy="private", tenant=None, picture_url=None, verification=None, last_modified=None)
        ]),
        (HubConnector, []),
        (HubConnector, [
            dict(id="123", name='Conn1', description=None, version='01', impact=1, parameters=[], readme_url=None, privacy_policy="private", tenant=None, picture_url=None, verification=None, last_modified=None)
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
