import warnings
from enum import auto

from geojson_pydantic import GeometryCollection
from pydantic import BaseModel
from strenum import PascalCaseStrEnum

warnings.filterwarnings("ignore", category=UserWarning)


class ValueType(PascalCaseStrEnum):
    NUMBER = auto()
    BOOLEAN = auto()
    STRING = auto()


class AttributeType(PascalCaseStrEnum):
    COMPUTED = auto()
    INPUT = auto()
    OUTPUT = auto()


class AssetKind(BaseModel):
    id: str | None = None
    name: str


class ResourceSummary(BaseModel):
    id: str | None = None
    name: str


class AssetParams(BaseModel):
    id: str | None = None
    name: str
    description: str | None = None
    tags: list[str] | None = None
    geometry: GeometryCollection | None = None
    centroid_coordinates: tuple[float, float] | None = None
    kind: AssetKind | None = None
    timezone: str | None = "UTC"


class Attribute(BaseModel):
    id: str | None = None
    name: str
    description: str | None = None
    type: ValueType
    unit: str | None = None
    origin: AttributeType


class Metadata(BaseModel):
    id: str
    name: str
    description: str | None = None
    value: float | int | str | bool | None = None
    type: ValueType
    unit: str | None = None


class AssetRelationship(BaseModel):
    id: str | None = None
    name: str
    description: str | None = None
    related_asset_kind: AssetKind | None = None
    asset: ResourceSummary | None = None
    related_asset: ResourceSummary | None = None
