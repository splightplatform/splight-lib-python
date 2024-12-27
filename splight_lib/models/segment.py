from splight_lib.models import AssetParams, AssetRelationship, Attribute
from splight_lib.models.database_base import SplightDatabaseBaseModel
from splight_lib.models.metadata import Metadata


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
