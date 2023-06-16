from typing import Any, Dict

from splight_lib.client.database.abstract import AbstractDatabaseClient
from splight_lib.client.database.local_client import LocalDatabaseClient
from splight_lib.client.database.remote_client import RemoteDatabaseClient


class DatabaseClientBuilder:
    @staticmethod
    def build(
        local: bool = False, parameters: Dict[str, Any] = {}
    ) -> AbstractDatabaseClient:
        if local:
            db_client = LocalDatabaseClient(**parameters)
        else:
            db_client = RemoteDatabaseClient(**parameters)
        return db_client
