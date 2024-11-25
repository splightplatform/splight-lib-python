from splight_lib.models import Asset, AssetParams, Attribute, Metadata
from splight_lib.models.database_base import SplightDatabaseBaseModel


class Segment(AssetParams, SplightDatabaseBaseModel):
    temperature: Attribute
    wind_direction: Attribute
    wind_speed: Attribute
    altitude: Metadata
    azimuth: Metadata
    cumulative_distance: Metadata
    reference_sag: Metadata
    reference_temperature: Metadata
    span_length: Metadata
    line: None | Asset
    grid: None | Asset
