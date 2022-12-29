import pysher
import requests
from furl import furl
from retry import retry
from typing import Callable, Dict
from splight_lib.logging import logging
from splight_abstract.communication import (
    AbstractCommunicationClient,
    ClientNotReady,
)
import logging
from splight_models.communication import CommunicationClientStatus, CommunicationContext, CommunicationEvent

from remote_splight_lib.auth.auth import SplightAuthToken
from remote_splight_lib.settings import settings
from remote_splight_lib.communication.classmap import CLASSMAP


logger = logging.getLogger()


class CommunicationFactory:

    def __init__(self, model):
        self._model = model

    def get_url(self):
        base_url = furl(settings.SPLIGHT_PLATFORM_API_HOST)
        return base_url / CLASSMAP.get(self._model)

    def get_headers(self):
        auth_token = SplightAuthToken(
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
        )
        return auth_token.header

    def create(self, data: Dict):
        response = requests.post(self.get_url(), json=data, headers=self.get_headers())
        assert response.status_code == 201, f"Cant create communication {self._model}."
        return self._model.parse_obj(response.json())

    def get(self, params=None):
        response = requests.get(self.get_url(), params=params, headers=self.get_headers())
        assert response.status_code == 200, f"Cant fetch communication {self._model}."
        data = response.json()
        return self._model.parse_obj(data)


class CommunicationClient(AbstractCommunicationClient):

    def __init__(self, daemon: bool = True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._status = CommunicationClientStatus.STOPPED
        self._channel_bindings = []
        self._client, self._context = None, None
        self._system_bindings = [
            ("pusher:connection_established", self.__on_connection_established),
            ("pusher:connection_failed", self.__on_connection_failed),
            ("pusher:error", self.__on_error),
        ]
        self._daemon = daemon
        try:
            self.__load_context()
            self.__load_client()
            self.__check_readiness()
        except Exception as e:
            logger.exception(e)
            logger.warning("Failed to start communication client. Moving forward without remote commands.")
            self._status = CommunicationClientStatus.ERROR

    @property
    def status(self):
        return self._status

    @property
    def context(self):
        return self._context

    @retry(ClientNotReady, tries=3, delay=2, jitter=1)
    def __check_readiness(self):
        if self.status != CommunicationClientStatus.READY:
            raise ClientNotReady

    @retry(Exception, tries=3, delay=2, jitter=1)
    def __load_context(self):
        params = {"instance_id": self.instance_id}
        self._context = CommunicationFactory(CommunicationContext).get(params)

    @retry(Exception, tries=3, delay=2, jitter=1)
    def __load_client(self):
        if not self._context:
            raise NotImplementedError
        self._client = pysher.Pusher(
            key=self._context.key,
            auth_endpoint=self._context.auth_endpoint,
            auth_endpoint_headers=self._context.auth_headers,
            user_data=self._context.channel_data.dict() if self.context.channel_data else None,
            daemon=self._daemon,
            log_level=logging.WARNING
        )
        self.__bind_system_events()
        self._client.connect()

    def __bind_system_events(self):
        if self._client is None:
            return
        for event, handler in self._system_bindings:
            self._client.connection.bind(event, handler)

    def __on_connection_established(self, data):
        self._channel = self._client.subscribe(self._context.channel)
        self._private_room_channel = self._client.subscribe(self._context.private_room_channel)
        for event_name, event_handler in self._channel_bindings:
            self._channel.bind(event_name, event_handler)
            self._private_room_channel.bind(event_name, event_handler)
        self._status = CommunicationClientStatus.READY

    def __on_connection_failed(self, data):
        self._status = CommunicationClientStatus.FAILED

    def __on_error(self, data):
        logger.error("Error on message", data)

    def bind(self, event_name: str, event_handler: Callable) -> None:
        self._channel_bindings.append((event_name, event_handler))
        if self.status != CommunicationClientStatus.READY:
            logger.warning("Bind events failed due to comm client is not ready")
            return
        self._channel.bind(event_name, event_handler)
        self._private_room_channel.bind(event_name, event_handler)

    def unbind(self, event_name: str, event_handler: Callable) -> None:
        # TODO implement this
        raise NotImplementedError

    def trigger(self, event: CommunicationEvent):
        return CommunicationFactory(CommunicationEvent).create(data=event.dict())

    def authenticate(self, channel_name: str, socket_id: str, custom_data: Dict = None) -> Dict:
        raise NotImplementedError
