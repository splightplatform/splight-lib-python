from typing import Any, Dict

from requests import Session


class BaseEndpoint:
    def __init__(self, base_url: str, session: Session):
        # Making sure url endswith /
        self._base_url = base_url if base_url.endswith("/") else f"{base_url}/"
        self._session = session

        self._url = f"{self._base_url}{self.PATH}"

    def _get(self, url: str):
        response = self._session.get(url)
        content = response.json() if response.content else None
        return content, response.status_code

    def _post(self, url: str, data: Dict):
        response = self._session.post(url, json=data)
        content = response.json() if response.content else None
        return content, response.status_code

    def _put(self, url: str, data: Dict):
        response = self._session.put(url, json=data)
        content = response.json() if response.content else None
        return content, response.status_code

    def _patch(self, url: str, data: Dict):
        response = self._session.patch(url, json=data)
        content = response.json() if response.content else None
        return content, response.status_code

    def _delete(self, url: str):
        response = self._session.delete(url)
        content = response.json() if response.content else None
        return content, response.status_code


class ListMixin:
    def list(self):
        return self._get(url=self._url)


class RetrieveMixin:
    def retrieve(self, resource_id: str):
        url = f"{self._url}{resource_id}/"
        return self._get(url=url)


class CreateMixin:
    def create(self, data: Dict[str, Any]):
        return self._post(url=self._url, data=data)


class UpdateMixin:
    def update(self, resource_id: str, data: Dict[str, Any]):
        url = f"{self._url}{resource_id}/"
        return self._put(url=url, data=data)


class DestroyMixin:
    def destroy(self, resource_id: str):
        url = f"{self._url}{resource_id}/"
        return self._delete(url=url)


class Credentials(BaseEndpoint, ListMixin, CreateMixin, DestroyMixin):
    PATH = "/credentials/"


class Profile(BaseEndpoint, ListMixin, UpdateMixin):
    PATH = "/me/"

    def organization(self):
        url = f"{self._url}get_organization/"
        return self._get(url)

    def update_profile(self, data: Dict[str, Any]):
        url = f"{self._url}set_profile/"
        return self._put(url=url, data=data)

    def update_organization(self, data: Dict[str, Any]):
        url = f"{self._url}set_organization_metadata/"
        return self._put(url=url, data=data)


class Organizations(BaseEndpoint, ListMixin, RetrieveMixin):
    PATH = "/organizations/"


class Roles(BaseEndpoint, ListMixin, RetrieveMixin):
    PATH = "/roles/"


class Users(BaseEndpoint, ListMixin, RetrieveMixin, CreateMixin, UpdateMixin):
    PATH = "/users/"
