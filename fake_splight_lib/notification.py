from typing import Dict

from splight_abstract import AbstractNotificationClient
from splight_lib import logging
from splight_models import Notification

logger = logging.getLogger()


class FakeNotificationClient(AbstractNotificationClient):
    @property
    def channel(self):
        return f"private-{self.namespace}"

    def send(self, instance: Notification, topic: str = "default") -> None:
        logger.info(
            f"[FAKED] Notification sent channel:{self.channel} topic:{topic} data:{instance.dict()} "
        )

    def authenticate(self, channel_name: str, socket_id: str) -> Dict:
        return {"auth": "1234"}
