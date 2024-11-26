from splight_lib.models import (
    AssetParams,
    AssetRelationship,
    Attribute,
    Metadata,
)
from splight_lib.models.database_base import SplightDatabaseBaseModel


class Segment(AssetParams, SplightDatabaseBaseModel):
    temperature: None | Attribute = None
    wind_direction: None | Attribute = None
    wind_speed: None | Attribute = None
    altitude: None | Metadata = None
    azimuth: None | Metadata = None
    cumulative_distance: None | Metadata = None
    reference_sag: None | Metadata = None
    reference_temperature: None | Metadata = None
    span_length: None | Metadata = None
    line: None | AssetRelationship = None
    grid: None | AssetRelationship = None
