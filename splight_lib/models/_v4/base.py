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
