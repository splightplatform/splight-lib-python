from .base import SplightBaseModel
from pydantic import Field, validator
from typing import Any, Dict, Optional


class Mapping(SplightBaseModel):
    id: Optional[str]


class ValueMapping(Mapping):
    asset_id: str
    attribute_id: str
    value: str
    name: Optional[str] = None
    description: Optional[str] = None

    @validator("name", always=True)
    def get_name(cls, name: str, values: Dict[str, Any]) -> str:
        if not name:
            return "ValueMapping " + values.get('value', "")
        return name


class ReferenceMapping(Mapping):
    asset_id: str
    attribute_id: str
    ref_asset_id: str
    ref_attribute_id: str
    name: Optional[str] = None
    description: Optional[str] = None

    @validator("name", always=True)
    def get_name(cls, name: str, values: Dict[str, Any]) -> str:
        if not name:
            return "ReferenceMapping"
        return name


class ClientMapping(Mapping):
    asset_id: str
    attribute_id: str
    connector_id: str
    path: str
    period: int = 5000
    name: Optional[str] = None
    description: Optional[str] = None

    @validator("name", always=True)
    def get_name(cls, name: str, values: Dict[str, Any]) -> str:
        if not name:
            return "ClientMapping " + values.get('path', "")
        return name


class ServerMapping(Mapping):
    asset_id: str
    attribute_id: str
    connector_id: str
    path: str
    name: Optional[str] = None
    description: Optional[str] = None

    @validator("name", always=True)
    def get_name(cls, name: str, values: Dict[str, Any]) -> str:
        if not name:
            return "ServerMapping " + values.get('path', "")
        return name