from typing import Dict

from furl import furl
from requests import Session

from remote_splight_lib.auth import SplightAuthToken
from remote_splight_lib.settings import settings
from splight_abstract.notification import AbstractNotificationClient
from splight_models import Notification


class NotificationClient(AbstractNotificationClient):

    _PREFIX = "notification"

    def __init__(self, namespace: str = "default"):

        super(NotificationClient, self).__init__(namespace=namespace)
        self._base_url = furl(settings.SPLIGHT_PLATFORM_API_HOST)
        token = SplightAuthToken(
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
        )
        self._session = Session()
        self._session.headers.update(token.header)

    def send(self, instance: Notification, topic: str = "default") -> None:
        url = self._base_url / f"{self._PREFIX}/"
        response = self._session.post(
            url,
            data=instance.dict()
        )
        response.raise_for_status()

    def authenticate(self, channel_name: str, socket_id: str) -> Dict:
        url = self._base_url / f"{self._PREFIX}/auth/"
        data = {
            "channel_name": channel_name,
            "socket_id": socket_id
        }
        response = self._session.post(
            url,
            data=data
        )
        response.raise_for_status()
        return response.json()
