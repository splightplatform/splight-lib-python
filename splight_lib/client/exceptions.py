from httpx import ConnectError, ReadTimeout
from requests.exceptions import ConnectionError, Timeout
from splight_lib.restclient import ConnectError as SplightConnectError
from splight_lib.restclient import HTTPError
from splight_lib.restclient import Timeout as TimeoutError

REQUEST_EXCEPTIONS = (ConnectionError, Timeout)
SPLIGHT_REQUEST_EXCEPTIONS = (
    HTTPError,
    TimeoutError,
    ConnectError,
    ReadTimeout,
    SplightConnectError,
)


class InvalidModelName(Exception):
    def __init__(self, model_name: str):
        self._msg = f"Model {model_name} is not a valid database model"

    def __str__(self) -> str:
        return self._msg


class InstanceNotFound(Exception):
    def __init__(self, name: str, uid: str):
        self._msg = f"Object {uid} of type {name} not found in database"

    def __str__(self) -> str:
        return self._msg
