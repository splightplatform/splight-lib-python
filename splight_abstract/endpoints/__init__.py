from typing import Any, Dict, Optional

from requests import Session
from simplejson.errors import JSONDecodeError


class BaseEndpoint:
    def __init__(self, base_url: str, session: Session):
        self._session = session
        self._base_url = base_url
        self._url = f"{self._base_url.strip('/')}/{self.PATH.strip('/')}/"

    def _request_content(self, response: Any):
        try:
            return response.json() if response.content else None
        except JSONDecodeError as e:
            raise Exception(str(response.content))

    def _get_request(self, url: str, params: Optional[Dict] = None):
        response = self._session.get(url, params=params)
        content = self._request_content(response)
        return content, response.status_code

    def _post_request(self, url: str, data: Dict):
        response = self._session.post(url, json=data)
        content = self._request_content(response)
        return content, response.status_code

    def _put_request(self, url: str, data: Dict):
        response = self._session.put(url, json=data)
        content = self._request_content(response)
        return content, response.status_code

    def _patch_request(self, url: str, data: Dict):
        response = self._session.patch(url, json=data)
        content = self._request_content(response)
        return content, response.status_code

    def _delete_request(self, url: str):
        response = self._session.delete(url)
        content = self._request_content(response)
        return content, response.status_code


class ListMixin:
    def list(self, params: Optional[Dict] = None):
        return self._get_request(url=self._url, params=params)


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


class PartialUpdateMixin:
    def partial_update(self, resource_id: str, data: Dict[str, Any]):
        url = f"{self._url}{resource_id}/"
        return self._patch_request(url=url, data=data)


class DestroyMixin:
    def destroy(self, resource_id: str):
        url = f"{self._url}{resource_id}/"
        return self._delete_request(url=url)
