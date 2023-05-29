from typing import Dict, List, Optional, Tuple, Type

import requests
from furl import furl
from pydantic import BaseModel
from splight_lib.auth import SplightAuthToken
from splight_lib.client.hub.abstract import (
    AbstractHubClient,
    AbstractHubSubClient,
    validate_client_resource_type,
)
from abc import ABC
from splight_lib.settings import settings


class _SplightHubGenericClient(AbstractHubSubClient):
    _PREFIX: str = "v2/hub"
    valid_classes = [
        'HubComponent',
        'HubComponentVersion',
    ]
    _CLASS_MAP = {
        'HubComponent': "components",
        'HubComponentVersion': "component-versions",
    }

    def __init__(
        self,
        base_path: str,
        headers: Optional[Dict[str, str]] = {},
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._base_url = furl(
            settings.SPLIGHT_PLATFORM_API_HOST,
            path=f"{self._PREFIX}/{base_path}/",
        )
        self._session = requests.Session()
        self._session.headers.update(headers)

    def _get_url(self, resource_type: str, id: Optional[str] = None) -> furl:
        resource_type_prefix = self._CLASS_MAP.get(resource_type.__name__)
        url = self._base_url / f"{resource_type_prefix}/"
        if id:
            url = url / f"{id}/"
        return url

    def _get_params(self, limit_: int, skip_: int, **kwargs):
        if limit_ > 0:
            kwargs["page_size"] = limit_
            if skip_ > 0:
                kwargs["page"] = skip_ // limit_ + 1
        return kwargs

    def save(self, instance: BaseModel) -> BaseModel:
        raise NotImplementedError

    @validate_client_resource_type
    def _get(
        self,
        resource_type: Type,
        first: bool = False,
        limit_: int = -1,
        skip_: int = 0,
        **kwargs,
    ) -> List[BaseModel]:
        url = self._get_url(resource_type)
        params = self._get_params(limit_, skip_, **kwargs)
        response = self._session.get(url, params=params)
        assert (
            response.status_code == 200
        ), f"Failed to get components {response.content}"
        queryset = [resource_type(**v) for v in response.json()["results"]]
        if first:
            return queryset[0] if queryset else None
        return queryset

    def count(
        self,
        resource_type: Type,
        first=False,
        limit_: int = -1,
        skip_: int = 0,
        **kwargs,
    ):
        url = self._get_url(resource_type)
        params = self._get_params(limit_=-1, skip_=-1, kwargs=kwargs)
        response = self._session.get(url, params=params)
        assert (
            response.status_code == 200
        ), f"Failed to get components {response.content}"
        return response.json()["count"]

    def delete(self, resource_type: Type, id: str) -> None:
        url = self._get_url(resource_type, id)
        response = self._session.delete(url)
        assert (
            response.status_code == 204
        ), f"Failed to delete component {response.content}"

    @validate_client_resource_type
    def update(self, resource_type: Type, id: str, data: Dict) -> BaseModel:
        url = self._get_url(resource_type, id)
        response = self._session.put(url, json=data)
        assert (
            response.status_code == 200
        ), f"Failed to update component. {response.content}"
        return resource_type(**response.json())

    @validate_client_resource_type
    def partial_update(
        self, resource_type: Type, id: str, data: Dict
    ) -> BaseModel:
        url = self._get_url(resource_type, id)
        response = self._session.patch(url, json=data)
        assert (
            response.status_code == 200
        ), f"Failed to update component. {response.content}"
        return resource_type.parse_obj(response.json())

    @validate_client_resource_type
    def rebuild(self, resource_type: Type, id: str) -> None:
        url = self._get_url(resource_type, id)
        url = url / "rebuild/"
        response = self._session.post(url, headers=self.headers)
        assert (
            response.status_code == 204
        ), f"Failed to rebuild component. {response.content}"


class SplightHubClient(ABC):
    def __init__(self, scope: str, resource_type: Type, *args, **kwargs) -> None:
        super().__init__()
        token = SplightAuthToken(
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
        )
        self._scopes = {
            'all': _SplightHubGenericClient(
                base_path="all", headers=token.header
            ),
            'mine': _SplightHubGenericClient(
                base_path="mine", headers=token.header
            ),
            'public': _SplightHubGenericClient(
                base_path="public", headers=token.header
            ),
            'private': _SplightHubGenericClient(
                base_path="private", headers=token.header
            ),
            'setup': _SplightHubGenericClient(
                base_path="setup", headers=token.header
            ),
        }
        self._host = furl(settings.SPLIGHT_PLATFORM_API_HOST)
        self._headers = token.header
        self._scope = scope
        self._resource_type = resource_type

    def upload(self, data: Dict, files: Dict) -> Tuple:
        url = self._host / "v2/hub/upload/"
        response = requests.post(
            url, files=files, data=data, headers=self._headers
        )
        status_code = response.status_code
        assert status_code == 201, "Unable to upload component to HUB"
        return response.json(), status_code

    def download(self, data: Dict) -> Tuple:
        url = self._host / "v2/hub/download/"
        response = requests.post(url, data=data, headers=self._headers)
        status_code = response.status_code
        assert status_code == 200, "Unable to download component"
        return response.content, status_code

    def list(self, **params):
        client = self._scopes.get(self._scope)
        instances = client.get(self._resource_type, **params)
        instances = [self._resource_type.parse_obj(item) for item in instances]
        return instances

    def retrieve(self, id: str):
        client = self._scopes.get(self._scope)
        instance = client.get(self._resource_type, id)
        return self._resource_type.parse_obj(instance) if instance else None

    def delete(self, id: str):
        client = self._scopes.get(self._scope)
        client.delete(self._resource_type, id)
