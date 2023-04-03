from requests.exceptions import ConnectionError, Timeout

REQUEST_EXCEPTIONS = (ConnectionError, Timeout)


class InvalidModel(Exception):
    def __init__(self, model_name: str):
        self._msg = f"Model {model_name} is not a valid database model"

    def __str__(self) -> str:
        return self._msg


class InstanceNotFound(Exception):
    def __init__(self, name: str, uid: str):
        self._msg = f"Object {uid} of type {name} not found in database"

    def __str__(self) -> str:
        return self._msg
