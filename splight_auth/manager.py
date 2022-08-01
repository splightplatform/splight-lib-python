from requests import Session

from client import AbstractClient

from .endpoints.endpoint import (
    Credentials,
    Organizations,
    Profile,
    Roles,
    Users,
)


class MethodNotAllowed(Exception):
    def __init__(self, method: str):
        self._msg = f"Method {method} not valid"

    def __str__(self) -> str:
        return self._msg


class AuthClient(AbstractClient):
    def __init__(self, url: str, headers):
        super().__init__()
        self._url = url

        session = Session()
        session.headers.update(headers)
        self.credentials = Credentials(base_url=self._url, session=session)
        self.profile = Profile(base_url=self._url, session=session)
        self.role = Roles(base_url=self._url, session=session)
        self.user = Users(base_url=self._url, session=session)
        self.organization = Organizations(base_url=self._url, session=session)
