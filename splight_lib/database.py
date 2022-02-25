
import ast
import os
from splight_models import (
    Trigger,
    TriggerGroup,
    Network,
    ClientConnector,
    ServerConnector,
    ClientMapping,
    ValueMapping,
    ReferenceMapping,
    ServerMapping,
    Asset,
    Attribute
)
from splight_database.django.client import DjangoClient
from fake_splight_lib.database import FakeDatabaseClient


DatabaseClient = DjangoClient

if ast.literal_eval(os.getenv("FAKE_DATABASE", "True")):
    DatabaseClient = FakeDatabaseClient

__all__ = [
    "Asset",
    "Attribute",
    "Trigger",
    "TriggerGroup",
    "Network",
    "ClientConnector",
    "ServerConnector",
    "ClientMapping",
    "ValueMapping",
    "ReferenceMapping",
    "ServerMapping",
    "DatabaseClient"
]
