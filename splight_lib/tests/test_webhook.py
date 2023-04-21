import os
from unittest import TestCase

from pytest import MonkeyPatch
from splight_lib.webhook import WebhookClient, WebhookEvent
from splight_models import Asset

MonkeyPatch().setenv("SPLIGHTD_WEBHOOK_SECRET", "SECRETNOTSECRET")


class TestShortcut(TestCase):
    def setUp(self) -> None:
        os.environ["SPLIGHTD_WEBHOOK_SECRET"] = "fake_secret"
        self._client = WebhookClient()
        return super().setUp()

    def test_construct_event_from_payload(self):
        data = {"name": "Asset1"}
        event = WebhookEvent(
            event_name="asset-create", object_type="Asset", data=data
        )
        payload, signature = self._client.construct_payload(event)
        event_from_payload = self._client.construct_event(
            payload=payload, signature=signature
        )
        self.assertEqual(event_from_payload, event)
        self.assertIsInstance(event_from_payload.object, Asset)
        self.assertEqual(event_from_payload.object.name, "Asset1")
