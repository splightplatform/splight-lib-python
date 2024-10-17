from geojson_pydantic import GeometryCollection

from splight_lib.models.database_base import (
    ResourceSummary,
    SplightDatabaseBaseModel,
)
from splight_lib.models.metadata import Metadata


class Line(SplightDatabaseBaseModel):
    id: str | None = None
    name: str
    description: str | None = None
    # tags: list[Tag] = []
    # attributes: list[Attribute] = []
    # metadata: list[Metadata] = []
    geometry: GeometryCollection | None = None
    centroid_coordinates: tuple[float, float] | None = None
    diameter: Metadata | None = None
