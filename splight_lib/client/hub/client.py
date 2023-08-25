from typing import Dict, List, Tuple

import requests
from furl import furl
from pydantic import BaseModel

from splight_lib.auth import SplightAuthToken
from splight_lib.client.hub.abstract import AbstractHubClient


class SplightHubClient(AbstractHubClient):
    _PREFIX: str = "v2/hub/component"
    _ORG_PREFIX = "v2/account/user/organizations"

    def __init__(
        self, access_key: str, secret_key: str, api_host: str
    ) -> None:
        token = SplightAuthToken(
            access_key=access_key,
            secret_key=secret_key,
        )

        self._hub_url = furl(api_host, path=f"{self._PREFIX}/")
        self._org_url = furl(api_host, path=f"{self._ORG_PREFIX}/")

        self._session = requests.Session()
        self._session.headers.update(token.header)

    @property
    def _org_id(self):
        response = self._session.get(self._org_url)
        org_id = response.json()["id"]
        assert (
            response.status_code == 200
        ), f"Failed to get organization id {response.content}"
        return org_id

    def _get_params(self, limit_: int, skip_: int, **kwargs):
        if limit_ > 0:
            kwargs["page_size"] = limit_
            if skip_ > 0:
                kwargs["page"] = skip_ // limit_ + 1
        return kwargs

    def _get(
        self,
        first: bool = False,
        limit_: int = -1,
        skip_: int = 0,
        **kwargs,
    ) -> List[BaseModel]:
        url = self._hub_url / "components"
        params = self._get_params(limit_, skip_, **kwargs)
        response = self._session.get(url, params=params)
        assert (
            response.status_code == 200
        ), f"Failed to get components {response.content}"
        queryset = response.json()["results"]
        if first:
            return queryset[0] if queryset else None
        return queryset

    def upload(self, data: Dict, files: Dict) -> Tuple:
        url = self._hub_url / "upload"
        response = requests.post(
            url,
            files=files,
            data=data,
        )
        status_code = response.status_code
        assert status_code == 201, "Unable to upload component to HUB"
        return response.json()

    def download(self, data: Dict) -> Tuple:
        url = self._hub_url / "download"
        response = requests.post(url, data=data, headers=self._headers)
        status_code = response.status_code
        assert status_code == 200, "Unable to download component"
        return response.content

    def delete(self, id: str) -> None:
        url = self._hub_url / "components" / id
        response = self._session.delete(url)
        assert (
            response.status_code == 204
        ), f"Failed to delete component {response.content}"

    def save(self, instance: BaseModel) -> BaseModel:
        raise NotImplementedError

    # TODO: deprecate
    def count(
        self,
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
