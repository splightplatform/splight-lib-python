from typing import Any, Dict

from splight_lib.client.database.abstract import AbstractDatabaseClient
from splight_lib.client.database.remote_client import RemoteDatabaseClient


class DatabaseClientBuilder:
    @staticmethod
    def build(parameters: Dict[str, Any] = {}) -> AbstractDatabaseClient:
        db_client = RemoteDatabaseClient(**parameters)
        return db_client
