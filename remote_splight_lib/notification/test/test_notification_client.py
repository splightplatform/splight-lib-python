from pytest import MonkeyPatch
MonkeyPatch().setenv("SPLIGHT_PLATFORM_HOST", "http://host:1234")
MonkeyPatch().setenv("SPLIGHT_ACCESS_ID", "access_id")
MonkeyPatch().setenv("SPLIGHT_SECRET_KEY", "secret_key")

from requests import Session
from unittest import TestCase
from unittest.mock import patch

from remote_splight_lib.notification import NotificationClient
from splight_models import Notification


class MockResponse:

    def raise_for_status(self):
        return None

    def json(self):
        return {
            "auth": "all good"
        }


class TestNotificationClient(TestCase):

    def get_client(self):
        client = NotificationClient()
        return client

    @patch.object(
        Session, "post", autospec=True  #, return_value=MockAttributeResponse()
    )
    def test_send_notification(self, mocked_method):
        client = self.get_client()
        resource = Notification.parse_obj(
            {
              "title": "string",
              "message": "string",
              "seen": True,
              "severity": "info",
              "asset_id": "string",
              "attribute_id": "string",
              "rule_id": "string",
              "source_id": "string",
              "source_type": "Algorithm"
            }
        )
        client.send(resource)
        mocked_method.assert_called()

    @patch.object(
        Session, "post", autospec=True, return_value=MockResponse()
    )
    def test_authenticate(self, mocked_method):
        client = self.get_client()
        auth = client.authenticate(channel_name="my-channel", socket_id="1234")
        mocked_method.assert_called()
