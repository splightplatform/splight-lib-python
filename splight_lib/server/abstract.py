import os
from abc import ABC
from typing import Optional

from pydantic import BaseModel
from pydantic_core import ValidationError

from splight_lib.logging._internal import LogTags, get_splight_logger
from splight_lib.restclient import ConnectError, HTTPError, Timeout
from splight_lib.server.spec import Spec

REQUEST_EXCEPTIONS = (ConnectError, HTTPError, Timeout)
logger = get_splight_logger("Base Server")


class SplightBaseServer(ABC):
    def __init__(
        self,
        server_id: Optional[str] = None,
    ):
        self._server_id = server_id

        self._spec = None
        self._config = None
        self._ports = None
        self._environment = None
        try:
            self._setup_server(server_id)
        except ValidationError as exc:
            logger.debug(
                "There was an error validating the server configuration"
            )
            logger.exception(exc, tags=LogTags.SERVER)
        except Exception as exc:
            logger.exception(exc, tags=LogTags.SERVER)

    def _setup_server(self, server_id: str):
        self._spec = self._load_spec()
        self._config = self._spec.server_config(server_id)
        self._ports = self._spec.ports
        self._environment = self._spec.environment

    @property
    def config(self) -> BaseModel:
        return self._config

    @property
    def ports(self) -> BaseModel:
        return self._ports

    @property
    def environment(self) -> BaseModel:
        return self._environment

    def _load_spec(self) -> Spec:
        """Loads the spec.json files located at the same level that the
        main file.
        """
        base_path = os.getcwd()
        spec = Spec.from_file(os.path.join(base_path, "spec.json"))
        return spec
