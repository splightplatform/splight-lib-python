from typing import Dict, List, Optional, Tuple, Type

import requests
from furl import furl
from pydantic import BaseModel

from remote_splight_lib.auth import SplightAuthToken
from remote_splight_lib.settings import settings
from splight_abstract import (
    AbstractHubClient,
    AbstractHubSubClient,
    validate_resource_type,
)
from splight_models import HubComponent, HubComponentVersion


class _SplightHubGenericClient(AbstractHubSubClient):
    _PREFIX: str = "v2/hub"
    valid_classes = [
        HubComponent,
        HubComponentVersion,
    ]
    _CLASS_MAP = {
        HubComponent: "components",
        HubComponentVersion: "component-versions",
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
        resource_type_prefix = self._CLASS_MAP.get(resource_type)
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

    @validate_resource_type
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

    @validate_resource_type
    def update(self, resource_type: Type, id: str, data: Dict) -> BaseModel:
        url = self._get_url(resource_type, id)
        response = self._session.put(url, json=data)
        assert (
            response.status_code == 200
        ), f"Failed to update component. {response.content}"
        return resource_type(**response.json())

    @validate_resource_type
    def partial_update(
        self, resource_type: Type, id: str, data: Dict
    ) -> BaseModel:
        url = self._get_url(resource_type, id)
        response = self._session.patch(url, json=data)
        assert (
            response.status_code == 200
        ), f"Failed to update component. {response.content}"
        return resource_type.parse_obj(response.json())

    @validate_resource_type
    def rebuild(self, resource_type: Type, id: str) -> None:
        url = self._get_url(resource_type, id)
        url = url / "rebuild/"
        response = self._session.post(url, headers=self.headers)
        assert (
            response.status_code == 204
        ), f"Failed to rebuild component. {response.content}"


class SplightHubClient(AbstractHubClient):

    def __init__(
        self, headers: Optional[Dict[str, str]] = {}, *args, **kwargs
    ) -> None:
        super().__init__()
        token = SplightAuthToken(
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
        )
        self._all = _SplightHubGenericClient(base_path="all", headers=headers)
        self._mine = _SplightHubGenericClient(
            base_path="mine", headers=token.header
        )
        self._public = _SplightHubGenericClient(
            base_path="public", headers=token.header
        )
        self._private = _SplightHubGenericClient(
            base_path="private", headers=token.header
        )
        self._setup = _SplightHubGenericClient(
            base_path="setup", headers=token.header
        )
        self._host = furl(settings.SPLIGHT_PLATFORM_API_HOST)
        self._headers = token.header

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

    def random_picture(self) -> Tuple:
        url = self._host / "hub/random_picture/"
        response = requests.get(url, headers=self._headers)
        status_code = response.status_code
        assert status_code == 200, "Unable to retrieve random picture"
        return response.content, status_code

    @property
    def all(self) -> AbstractHubSubClient:
        return self._all

    @property
    def mine(self) -> AbstractHubSubClient:
        return self._mine

    @property
    def public(self) -> AbstractHubSubClient:
        return self._public

    @property
    def private(self) -> AbstractHubSubClient:
        return self._private

    @property
    def setup(self) -> AbstractHubSubClient:
        return self._setup
