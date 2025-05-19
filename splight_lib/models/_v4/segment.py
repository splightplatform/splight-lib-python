from splight_lib.models._v4.asset import AssetParams, AssetRelationship
from splight_lib.models._v4.attribute import Attribute
from splight_lib.models._v4.metadata import Metadata
from splight_lib.models.database import SplightDatabaseBaseModel


class Segment(AssetParams, SplightDatabaseBaseModel):
    # Computed attributes
    ampacity_aar: Attribute | None = None
    ampacity_aar_lte: Attribute | None = None
    ampacity_aar_ste: Attribute | None = None
    ampacity_dlr: Attribute | None = None
    ampacity_dlr_lte: Attribute | None = None
    ampacity_dlr_ste: Attribute | None = None
    conductor_temperature: Attribute | None = None
    irradiance: Attribute | None = None
    temperature: Attribute | None = None
    wind_direction: Attribute | None = None
    wind_speed: Attribute | None = None

    # Metadata
    altitude: Metadata | None = None
    azimuth: Metadata | None = None
    cumulative_distance: Metadata | None = None
    line_altitude: Metadata | None = None
    reference_sag: Metadata | None = None
    reference_temperature: Metadata | None = None
    span_length: Metadata | None = None

    # Relationships
    line: AssetRelationship | None = None
