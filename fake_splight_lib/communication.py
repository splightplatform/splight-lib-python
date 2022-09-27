from typing import Callable

from splight_lib.logging import logging
from splight_abstract.communication import AbstractCommunicationClient, CommunicationContext


logger = logging.getLogger()


class FakeCommunicationClient(AbstractCommunicationClient):
    @property
    def context(self):
        return CommunicationContext(
            auth_headers=None,
            auth_endpoint=None,
            key='key',
            channel='default',
            user_data=None
        )

    @property
    def status(self):
        return 'ready'

    def remove_handler(self, event_name: str, event_handler: Callable):
        pass

    def add_handler(self, event_name: str, event_handler: Callable):
        pass
