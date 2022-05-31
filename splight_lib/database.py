import os
from fake_splight_lib.database import FakeDatabaseClient
from splight_database.django.client import DjangoClient

SELECTOR = {
    'fake': FakeDatabaseClient,
    'postgres': DjangoClient,
    'sqlite': DjangoClient,
}

DatabaseClient = SELECTOR.get(os.environ.get('DATABASE', 'fake'))

__all__ = [
    "DatabaseClient",
]
