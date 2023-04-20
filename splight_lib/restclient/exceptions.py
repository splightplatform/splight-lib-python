"""
Splight RestClient own exceptions.

Currently, based on httpx._exceptions
"""

from typing import Optional

from httpx._models import Request


class HTTPError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self._request = None

    @property
    def request(self) -> Request:
        if self._request is None:
            raise RuntimeError("The .request property has not been set.")
        return self._request

    @request.setter
    def request(self, request: Request) -> None:
        self._request = request


class RequestError(HTTPError):
    def __init__(
        self, message: str, *, request: Optional[Request] = None
    ) -> None:
        super().__init__(message)
        self._request = request


class Timeout(RequestError):
    """The base class for timeout errors.

    An operation has timed out.
    """


class ConnectError(RequestError):
    """Failed to establish a connection."""
