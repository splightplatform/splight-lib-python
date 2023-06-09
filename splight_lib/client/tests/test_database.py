from unittest import TestCase
from unittest.mock import patch

from splight_lib.client.database.remote_client import RemoteDatabaseClient


class TestRemoteDatabaseClient(TestCase):
    def setUp(self):
        self.patcher1 = patch(
            "splight_lib.client.database.remote_client.SplightAuthToken"
        )
        self.patcher2 = patch(
            "splight_lib.client.database.remote_client.SplightRestClient"
        )

        self.mock_auth_token = self.patcher1.start()
        self.mock_rest_client = self.patcher2.start()

        self.client = RemoteDatabaseClient(
            base_url="http://test.com",
            access_id="test_id",
            secret_key="test_secret",
        )

    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()

    def test_initialization(self):
        self.mock_auth_token.assert_called_once_with(
            access_key="test_id", secret_key="test_secret"
        )
        assert self.client._base_url.url == "http://test.com"
        self.mock_rest_client().update_headers.assert_called_once()
