import os

from splight_lib.models import Server
from splight_lib.server.exceptions import MissingInstanceEnvVar

ENV_VAR = "SPLIGHT_SERVER_ID"


class ServerLoader:
    @classmethod
    def from_env(cls) -> Server:
        if not (instance_id := os.environ.get(ENV_VAR)):
            raise MissingInstanceEnvVar(ENV_VAR)
        server = Server.retrieve(instance_id)
        return server
