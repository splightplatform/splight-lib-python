
import ast
import os
from splight_models import (
    Algorithm,
    Asset,
    Attribute,
    ClientConnector,
    ClientMapping,
    Channel,
    Network,
    TriggerNotification,
    ReferenceMapping,
    ServerConnector,
    ServerMapping,
    Trigger,
    TriggerGroup,
    ValueMapping,
    Tag,
    Runner
)
from splight_database.django.client import DjangoClient
from fake_splight_lib.database import FakeDatabaseClient


DatabaseClient = DjangoClient

if ast.literal_eval(os.getenv("FAKE_DATABASE", "True")):
    DatabaseClient = FakeDatabaseClient

__all__ = [
    "Algorithm",
    "Asset",
    "Attribute",
    "ClientConnector",
    "ClientMapping",
    "Channel",
    "DatabaseClient",
    "Network",
    "TriggerNotification",
    "ReferenceMapping",
    "ServerConnector",
    "ServerMapping",
    "Trigger",
    "TriggerGroup",
    "ValueMapping",
    "Tag",
    "Runner"
]
