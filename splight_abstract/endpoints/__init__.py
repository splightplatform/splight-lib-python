from typing import Any, Dict
from requests import Session


class BaseEndpoint:
    def __init__(self, base_url: str, session: Session):
        self._session = session
        self._base_url = base_url
        self._url = f"{self._base_url.strip('/')}/{self.PATH.strip('/')}/"

    def _get_request(self, url: str):
        response = self._session.get(url)
        content = response.json() if response.content else None
        return content, response.status_code

    def _post_request(self, url: str, data: Dict):
        response = self._session.post(url, json=data)
        content = response.json() if response.content else None
        return content, response.status_code

    def _put_request(self, url: str, data: Dict):
        response = self._session.put(url, json=data)
        content = response.json() if response.content else None
        return content, response.status_code

    def _patch_request(self, url: str, data: Dict):
        response = self._session.patch(url, json=data)
        content = response.json() if response.content else None
        return content, response.status_code

    def _delete_request(self, url: str):
        response = self._session.delete(url)
        content = response.json() if response.content else None
        return content, response.status_code


class ListMixin:
    def list(self):
        return self._get_request(url=self._url)


class RetrieveMixin:
    def retrieve(self, resource_id: str):
        url = f"{self._url}{resource_id}/"
        return self._get_request(url=url)


class CreateMixin:
    def create(self, data: Dict[str, Any]):
        return self._post_request(url=self._url, data=data)


class UpdateMixin:
    def update(self, resource_id: str, data: Dict[str, Any]):
        url = f"{self._url}{resource_id}/"
        return self._put_request(url=url, data=data)


class DestroyMixin:
    def destroy(self, resource_id: str):
        url = f"{self._url}{resource_id}/"
        return self._delete_request(url=url)
