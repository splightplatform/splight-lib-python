from unittest import TestCase
from unittest.mock import patch

from splight_auth.manager import AuthClient, Session


class TestAuthClient(TestCase):
    def get_client(self):
        return AuthClient(url="http://localhost:1234")

    @patch.object(Session, "get", autospec=True)
    def test_list_credentials(self, mocked_method):
        client = self.get_client()
        client.credentials.list()
        mocked_method.assert_called()

    @patch.object(Session, "post", autospec=True)
    def test_create_credential(self, mocked_method):
        client = self.get_client()
        client.credentials.create(data={"key": "value"})
        mocked_method.assert_called()

    @patch.object(Session, "delete", autospec=True)
    def test_delete_credential(self, mocked_method):
        client = self.get_client()
        client.credentials.destroy(resource_id="1234")
        mocked_method.assert_called()

    @patch.object(Session, "get", autospec=True)
    def test_list_profiles(self, mocked_method):
        client = self.get_client()
        client.profile.list()
        mocked_method.assert_called()

    @patch.object(Session, "get", autospec=True)
    def test_get_profile_organization(self, mocked_method):
        client = self.get_client()
        client.profile.organization()
        mocked_method.assert_called()

    @patch.object(Session, "put", autospec=True)
    def test_update_profile(self, mocked_method):
        client = self.get_client()
        client.profile.update_profile(data={"key": "value"})
        mocked_method.assert_called()

    @patch.object(Session, "put", autospec=True)
    def test_update_profile_organization(self, mocked_method):
        client = self.get_client()
        client.profile.update_organization(data={"key": "value"})
        mocked_method.assert_called()
