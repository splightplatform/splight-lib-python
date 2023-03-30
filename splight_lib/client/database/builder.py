from splight_abstract.database import AbstractDatabaseClient
from splight_lib.client.database import (
    LocalDatabaseClient,
    RemoteDatabaseClient,
)


class DatabaseClientBuilder:
    @staticmethod
    def build(
        namespace: str, local_db: bool = False, **kwargs
    ) -> AbstractDatabaseClient:
        if local_db:
            client = LocalDatabaseClient(namespace, **kwargs)
        else:
            client = RemoteDatabaseClient(namespace)
        return client
