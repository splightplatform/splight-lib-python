from pydantic import BaseModel
from requests import Session
from furl import furl
from typing import Type, List, Optional
from remote_splight_lib.auth.auth import SplightAuthToken
from splight_abstract.deployment.abstract import AbstractDeploymentClient
from remote_splight_lib.settings import settings
from splight_abstract.remote.abstract import AbstractRemoteClient
from splight_models.deployment import Deployment
from retry import retry
from requests.exceptions import (
    ConnectionError,
    Timeout
)
REQUEST_EXCEPTIONS = (ConnectionError, Timeout)


class DeploymentClient(AbstractDeploymentClient, AbstractRemoteClient):
    PATH = 'deployment'

    def __init__(self, namespace: str = "default", *args, **kwargs):
        super().__init__(namespace, *args, **kwargs)
        self._base_url = furl(settings.SPLIGHT_PLATFORM_API_HOST)
        token = SplightAuthToken(
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
        )
        self._session = Session()
        self._session.headers.update(token.header)

    def save(self, instance: BaseModel) -> BaseModel:
        raise NotImplementedError

    @retry(REQUEST_EXCEPTIONS, tries=3, delay=1)
    def _get(self, resource_type: Type, id: str = '', first=False, limit_: int = -1, skip_: int = 0, **kwargs) -> List[BaseModel]:

        if resource_type != Deployment:
            raise NotImplementedError
        response = self._list(
            first=first,
            limit_=limit_,
            skip_=skip_,
            **kwargs,
        )
        parsed = [
            resource_type.parse_obj(resource)
            for resource in response["results"]
        ]
        return parsed

    @retry(REQUEST_EXCEPTIONS, tries=3, delay=1)
    def _list(self, **kwargs):
        url = self._base_url / f"{self.PATH}/"
        params = self._parse_params(**kwargs)
        response = self._session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def delete(self, resource_type: Type, id: str) -> None:
        raise NotImplementedError

    def get_deployment_logs(self, id: str, limit: Optional[int] = None, since: Optional[str] = None, previous: bool = False) -> List[str]:
        raise NotImplementedError

    def get_capacity_options(self):
        raise NotImplementedError

    @classmethod
    def verify_header(cls, payload: bytes, signature: str) -> None:
        pass
