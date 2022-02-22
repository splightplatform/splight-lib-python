from pydantic import BaseModel
from typing import Optional


class Mapping(BaseModel):
    id: Optional[str]


class ValueMapping(Mapping):
    asset_id: str
    attribute_id: str
    value: str


class ReferenceMapping(Mapping):
    asset_id: str
    attribute_id: str
    value: str
    ref_asset_id: str
    ref_attribute_id: str


class ClientMapping(Mapping):
    asset_id: str
    attribute_id: str
    connector_id: str
    path: str


class ServerMapping(Mapping):
    asset_id: str
    attribute_id: str
    connector_id: str
    path: str
