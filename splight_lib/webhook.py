import json
from functools import cached_property
from pydantic import BaseSettings
from splight_lib.auth import HmacSignature
from splight_models import WebhookEvent


class WebhookSettings(BaseSettings):
    SPLIGHTD_WEBHOOK_SECRET: str


class WebhookClient:
    def __init__(self) -> None:
        self._settings = WebhookSettings()

    @cached_property
    def settings(self):
        return self._settings

    @staticmethod
    def construct_payload(event: WebhookEvent) -> bytes:
        """Creates an encoded payload based on a webhook event.

        Parameter
        ---------
        event : WebhookEvent

        Returns
        -------
        bytes
            the ascii encoded payload
        """
        return event.json().encode("ascii")

    @staticmethod
    def construct_event(payload: bytes) -> WebhookEvent:
        event = WebhookEvent.from_event_dict(
            json.loads(payload.decode("utf-8"))
        )
        return event

    @staticmethod
    def validate_signature(payload: bytes, signature: str) -> bool:
        return HmacSignature.verify_header(
            payload, signature, WebhookSettings.SPLIGHTD_WEBHOOK_SECRET
        )

    @staticmethod
    def get_signature(payload: bytes) -> str:
        """
        payload is an ascii encoded string
        """
        hmac = HmacSignature(
            secret=WebhookSettings.SPLIGHTD_WEBHOOK_SECRET
        )
        signature = hmac.compute_header_signature(payload)
        return signature
