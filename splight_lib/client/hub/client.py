from typing import Dict, List, Optional, Tuple

import requests
from furl import furl
from pydantic import BaseModel
from splight_lib.auth import SplightAuthToken
from splight_lib.client.hub.abstract import (
    AbstractHubClient,
    AbstractHubSubClient,
)


class _SplightHubGenericClient(AbstractHubSubClient):
    _PREFIX: str = "v2/hub"
    _CLASS_MAP = {
        "HubComponent": "components",
        "HubComponentVersion": "component-versions",
    }

    def __init__(
        self,
        base_path: str,
        api_host: str,
        headers: Optional[Dict[str, str]] = {},
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._base_url = furl(
            api_host,
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

    def _get(
        self,
        resource_type: str,
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
        queryset = response.json()["results"]
        if first:
            return queryset[0] if queryset else None
        return queryset

    def count(
        self,
        resource_type: str,
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

    def delete(self, resource_type: str, id: str) -> None:
        url = self._get_url(resource_type, id)
        response = self._session.delete(url)
        assert (
            response.status_code == 204
        ), f"Failed to delete component {response.content}"

    def update(self, resource_type: str, id: str, data: Dict) -> BaseModel:
        url = self._get_url(resource_type, id)
        response = self._session.put(url, json=data)
        assert (
            response.status_code == 200
        ), f"Failed to update component. {response.content}"
        return resource_type(**response.json())

    def partial_update(
        self, resource_type: str, id: str, data: Dict
    ) -> BaseModel:
        url = self._get_url(resource_type, id)
        response = self._session.patch(url, json=data)
        assert (
            response.status_code == 200
        ), f"Failed to update component. {response.content}"
        return resource_type.parse_obj(response.json())

    def rebuild(self, resource_type: str, id: str) -> None:
        url = self._get_url(resource_type, id)
        url = url / "rebuild/"
        response = self._session.post(url, headers=self.headers)
        assert (
            response.status_code == 204
        ), f"Failed to rebuild component. {response.content}"


class SplightHubClient(AbstractHubClient):
    def __init__(
        self, access_key: str, secret_key: str, api_host: str, *args, **kwargs
    ) -> None:
        super().__init__()
        token = SplightAuthToken(
            access_key=access_key,
            secret_key=secret_key,
        )
        self._all = _SplightHubGenericClient(
            base_path="all", headers=token.header, api_host=api_host
        )
        self._mine = _SplightHubGenericClient(
            base_path="mine", headers=token.header, api_host=api_host
        )
        self._public = _SplightHubGenericClient(
            base_path="public", headers=token.header, api_host=api_host
        )
        self._private = _SplightHubGenericClient(
            base_path="private", headers=token.header, api_host=api_host
        )
        self._setup = _SplightHubGenericClient(
            base_path="setup", headers=token.header, api_host=api_host
        )
        self._host = furl(api_host)
        self._headers = token.header

    def upload(self, data: Dict, files: Dict) -> Tuple:
        url = self._host / "v2/hub/upload/"
        response = requests.post(
            url, files=files, data=data, headers=self._headers
        )
        status_code = response.status_code
        assert status_code == 201, "Unable to upload component to HUB"
        return response.json()

    def download(self, data: Dict) -> Tuple:
        url = self._host / "v2/hub/download/"
        response = requests.post(url, data=data, headers=self._headers)
        status_code = response.status_code
        assert status_code == 200, "Unable to download component"
        return response.content

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
