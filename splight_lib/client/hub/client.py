from tempfile import NamedTemporaryFile
from typing import Any, Dict, Generator, List, Optional, TypedDict

import progressbar
import requests
from furl import furl
from pydantic import BaseModel

from splight_lib.auth import SplightAuthToken
from splight_lib.client.exceptions import RequestError
from splight_lib.client.hub.abstract import AbstractHubClient


class PaginatedResponse(TypedDict):
    count: int
    next: Optional[str]
    previous: Optional[str]
    results: List[Any]


class SplightHubClient(AbstractHubClient):
    _PREFIX: str = "v2/hub/component"
    _ORG_PREFIX = "v2/account/user/organizations"

    def __init__(
        self, api_host: str, access_key: str, secret_key: str
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
        ), f"Failed to get organization id: {response.json()}"
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
        url = self._hub_url / "versions/"
        params = self._get_params(limit_, skip_, **kwargs)
        instances = []
        for page in self._pages(url, page=1, **params):
            instances.extend(page["results"])
        if first:
            return instances[0] if instances else None
        return instances

    def get_org_id(self):
        return self._org_id

    def _create(self, instance: Dict) -> Dict:
        url = self._hub_url / "components/"
        response = self._session.post(url, json=instance)
        response.raise_for_status()
        instance = response.json()
        return instance

    def _update(self, instance: Dict) -> Dict:
        instance_id = instance.get("id")
        url = self._hub_url / "versions" / f"{instance_id}/"
        response = self._session.put(url, json=instance)
        response.raise_for_status()
        instance = response.json()
        return instance

    def build(self, id: str):
        url = self._hub_url / f"versions/{id}/build/"
        response = self._session.post(url)
        response.raise_for_status()

    def upload(self, id: str, file_path: str, type_: str):
        url = self._hub_url / f"versions/{id}/upload_url/"
        params = {"type": type_}
        response = self._session.get(url, params=params)
        response.raise_for_status()
        upload_url = response.json().get("url")

        with open(file_path, "rb") as fid:
            response = requests.put(upload_url, data=fid)
            if not response.ok:
                raise RequestError(response.status_code, response.text)

    def download(self, id: str, name: str, type: str) -> NamedTemporaryFile:
        url = self._hub_url / f"versions/{id}/download_url/"
        params = {"type": type}
        response = self._session.get(url, params=params)
        response.raise_for_status()
        download_url = response.json().get("url")

        file = NamedTemporaryFile(mode="wb+", suffix=name)
        # TODO: Check why python wget is raised and error with code 403
        response = requests.get(download_url, stream=True)
        with open(file.name, "wb") as f:
            length = int(response.headers.get("content-length"))
            chunk_size = 8192
            total_chunks = length // chunk_size + 1
            widgets = ["Downloading: ", progressbar.Bar("#")]
            bar = progressbar.ProgressBar(
                max_value=total_chunks, widgets=widgets
            ).start()
            for counter, chunk in enumerate(
                response.iter_content(chunk_size=chunk_size)
            ):
                f.write(chunk)
                bar.update(counter)
        return file

    def delete(self, id: str) -> None:
        url = self._hub_url / f"components/{id}/"
        response = self._session.delete(url)
        assert (
            response.status_code == 204
        ), f"Failed to delete component: {response.json()}"

    def save(self, instance: Dict) -> Dict:
        if instance.get("id"):
            return self._update(instance)
        else:
            return self._create(instance)

    def _pages(
        self, url: furl, **kwargs
    ) -> Generator[PaginatedResponse, None, None]:
        next_page = kwargs["page"]
        while next_page:
            response = self._list(url, **kwargs)
            yield response
            next_page = (
                furl(response["next"]).query.params["page"]
                if response["next"]
                else None
            )
            kwargs["page"] = next_page

    def _list(self, url: furl, **kwargs) -> PaginatedResponse:
        params = self._parse_params(**kwargs)
        response = self._session.get(url, params=params)
        if not response.ok:
            raise RequestError(response.status_code, response.text)
        return response.json()

    def _parse_params(self, **kwargs):
        params = {}
        for key, value in kwargs.items():
            if value is None:
                continue
            params[key] = value
            if isinstance(value, list):
                params[key] = ",".join(value)
        return params
