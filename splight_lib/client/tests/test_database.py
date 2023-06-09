from unittest import TestCase
from unittest.mock import MagicMock, patch

from splight_lib.client.database.remote_client import RemoteDatabaseClient
from splight_lib.client.exceptions import InvalidModelName


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

    def test_save_without_id(self):
        mock_instance = {"name": "instance_name"}
        self.client._create = MagicMock()
        self.client.save("alert", mock_instance)
        self.client._create.assert_called_once_with("alert", mock_instance)

    def test_save_with_id(self):
        mock_instance = {"id": "instance_id", "name": "instance_name"}
        self.client.save("alert", mock_instance)

    def test_delete(self):
        self.client.delete("alert", "instance_id")
        self.mock_rest_client().delete.assert_called_once()

    def test_delete_invalid_model_name(self):
        with self.assertRaises(InvalidModelName):
            self.client.delete("invalid_resource_name", "instance_id")

    @patch.object(RemoteDatabaseClient, "_retrieve_single")
    def test_get_with_id(self, mock_retrieve):
        mock_instance_id = "123"
        self.client._get("alert", id=mock_instance_id)
        mock_retrieve.assert_called_once_with("alert", id=mock_instance_id)

    @patch.object(RemoteDatabaseClient, "_retrieve_multiple")
    def test_get_without_id(self, mock_retrieve):
        self.client._get("alert")
        mock_retrieve.assert_called_once_with("alert", first=False)

    @patch.object(RemoteDatabaseClient, "_retrieve_multiple")
    def test_get_without_id_and_set_first(self, mock_retrieve):
        self.client._get("alert", first=True)
        mock_retrieve.assert_called_once_with("alert", first=True)
