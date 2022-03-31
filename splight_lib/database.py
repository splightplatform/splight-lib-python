
import ast
import os

from fake_splight_lib.database import FakeDatabaseClient
from splight_database.django.client import DjangoClient

DatabaseClient = DjangoClient

if ast.literal_eval(os.getenv("FAKE_DATABASE", "True")):
    DatabaseClient = FakeDatabaseClient

__all__ = [
    "DatabaseClient",
]
