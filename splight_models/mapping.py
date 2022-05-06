from .base import SplightBaseModel
from typing import Optional


class Mapping(SplightBaseModel):
    id: Optional[str]


class ValueMapping(Mapping):
    asset_id: str
    attribute_id: str
    value: str


class ReferenceMapping(Mapping):
    asset_id: str
    attribute_id: str
    ref_asset_id: str
    ref_attribute_id: str


class ClientMapping(Mapping):
    asset_id: str
    attribute_id: str
    connector_id: str
    path: str
    period: int = 5000


class ServerMapping(Mapping):
    asset_id: str
    attribute_id: str
    connector_id: str
    path: str
