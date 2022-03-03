
import ast
import os
from splight_models import (
    Asset,
    Attribute,
    ClientConnector,
    ClientMapping,
    Network,
    Notification,
    ReferenceMapping,
    ServerConnector,
    ServerMapping,
    Trigger,
    TriggerGroup,
    ValueMapping
)
from splight_database.django.client import DjangoClient
from fake_splight_lib.database import FakeDatabaseClient


DatabaseClient = DjangoClient

if ast.literal_eval(os.getenv("FAKE_DATABASE", "True")):
    DatabaseClient = FakeDatabaseClient

__all__ = [
    "Asset",
    "Attribute",
    "ClientConnector",
    "ClientMapping",
    "DatabaseClient",
    "Network",
    "Notification",
    "ReferenceMapping",
    "ServerConnector",
    "ServerMapping",
    "Trigger",
    "TriggerGroup",
    "ValueMapping"
]
