from remote_splight_lib.database import DatabaseClient
from splight_abstract.database import AbstractDatabaseClient
from splight_lib.client.database import LocalDatabaseClient


class DatabaseClientBuilder:
    @staticmethod
    def build(
        namespace: str, dev_mode: bool = False, **kwargs
    ) -> AbstractDatabaseClient:
        if dev_mode:
            client = LocalDatabaseClient(namespace, **kwargs)
        else:
            client = DatabaseClient(namespace)
        return client
