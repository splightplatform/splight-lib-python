import pytest

from splight_lib.client.database.abstract import AbstractDatabaseClient
from splight_lib.client.datalake.abstract import AbstractDatalakeClient


@pytest.fixture(autouse=True)
def reset_singletons():
    AbstractDatabaseClient._instances = {}
    AbstractDatalakeClient._instances = {}
