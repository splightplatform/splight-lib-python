import json
from typing import Callable, Dict

from splight_lib.logging import logging
from splight_abstract.communication import AbstractCommunicationClient, CommunicationContext
from splight_models.communication import CommunicationEvent


logger = logging.getLogger()


class FakeCommunicationClient(AbstractCommunicationClient):
    @property
    def context(self):
        return CommunicationContext(
            auth_headers=None,
            auth_endpoint=None,
            key='key',
            channel='default',
            channel_data=None
        )

    @property
    def status(self):
        return 'ready'

    @property
    def channel(self):
        return 'channel'

    def unbind(self, event_name: str, event_handler: Callable):
        logger.debug(f"[FAKED] unbind {event_name} {event_handler}")

    def bind(self, event_name: str, event_handler: Callable):
        logger.debug(f"[FAKED] bind {event_name} {event_handler}")

    def trigger(self, event: CommunicationEvent):
        logger.debug(f"[FAKED] trigger {event.event_name} {event.data} {event.socket_id} {event.instance_id}")

    def authenticate(self, channel_name: str, socket_id: str, custom_data: Dict = None) -> Dict:
        logger.debug(f"[FAKED] authenticate {channel_name} {socket_id} {custom_data}")
        return {
            "auth": "asd",
            "socket_id": socket_id,
            "channel_data": json.dumps(custom_data),
            "channel_name": channel_name
        }
