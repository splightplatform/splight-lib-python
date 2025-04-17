from splight_lib.models._v3.asset import (
    AssetParams,
    AssetRelationship,
    Attribute,
)
from splight_lib.models._v3.metadata import Metadata
from splight_lib.models.database import SplightDatabaseBaseModel


class Segment(AssetParams, SplightDatabaseBaseModel):
    temperature: Attribute | None = None
    wind_direction: Attribute | None = None
    wind_speed: Attribute | None = None
    altitude: Metadata | None = None
    azimuth: Metadata | None = None
    cumulative_distance: Metadata | None = None
    reference_sag: Metadata | None = None
    reference_temperature: Metadata | None = None
    span_length: Metadata | None = None
    line: AssetRelationship | None = None
    grid: AssetRelationship | None = None
