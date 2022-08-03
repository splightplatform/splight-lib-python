from typing import Dict, Optional

from requests import Session

from client import AbstractClient

from .endpoints.endpoint import (
    Credentials,
    Organizations,
    Profile,
    Roles,
    SuperAdmin,
    Users,
)


class MethodNotAllowed(Exception):
    def __init__(self, method: str):
        self._msg = f"Method {method} not valid"

    def __str__(self) -> str:
        return self._msg


class AuthClient(AbstractClient):
    """Class responsible for interacting with a Auth API.

    Attributes
    ----------
    credentials
    profile
    role
    user
    organization
    """

    def __init__(self, url: str, headers: Optional[Dict[str, str]] = None):
        """Class constructor

        Parameters
        ----------
        url : str
            The URL for the Auth API.
        headers : Optional[Dict[str, str]]
            A dict with the headers to be used in the requests to the Auth API
        """
        super().__init__()
        self._url = url

        session = Session()
        if headers:
            session.headers.update(headers)
        self.credentials = Credentials(base_url=self._url, session=session)
        self.profile = Profile(base_url=self._url, session=session)
        self.role = Roles(base_url=self._url, session=session)
        self.user = Users(base_url=self._url, session=session)
        self.organization = Organizations(base_url=self._url, session=session)
        self.superadmin = SuperAdmin(base_url=self._url, session=session)
