from pydantic import BaseModel
from typing import Optional
from enum import Enum


class Protocol(Enum):
    DNP3 = "DNP3"
    IEC61850 = "IEC61850"


class Connector(BaseModel):
    id: Optional[str]
    name: str
    description: Optional[str]  = None
    host: str
    port: int
    protocol: str
    extra_properties: Optional[str]


class ClientConnector(Connector):
    network_id: Optional[str]


class ServerConnector(Connector):
    network_id: Optional[str]
    external_port: Optional[int]
