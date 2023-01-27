import json
from typing import Tuple
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

    def construct_payload(self, event: WebhookEvent) -> Tuple[bytes, bytes]:
        payload = event.json().encode("utf-8")
        signature = self.get_signature(payload)
        return payload, signature

    def construct_event(self, payload: bytes, signature: str) -> WebhookEvent:
        self.validate_signature(payload, signature)
        event_dict = json.loads(payload.decode("utf-8"))
        event = WebhookEvent.parse_obj(event_dict)
        return event

    def validate_signature(self, payload: bytes, signature: str) -> bool:
        return HmacSignature.verify_header(
            payload, signature, self._settings.SPLIGHTD_WEBHOOK_SECRET
        )

    def get_signature(self, payload: bytes) -> str:
        hmac = HmacSignature(
            secret=self._settings.SPLIGHTD_WEBHOOK_SECRET
        )
        signature = hmac.compute_header_signature(payload)
        return signature
