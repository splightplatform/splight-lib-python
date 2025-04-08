from splight_lib.models._v4.asset import AssetRelationship
from splight_lib.models._v4.attribute import Attribute
from splight_lib.models._v4.base import AssetParams
from splight_lib.models._v4.metadata import Metadata
from splight_lib.models.database import SplightDatabaseBaseModel


class Bus(AssetParams, SplightDatabaseBaseModel):
    # Input attributes
    active_power: Attribute | None = None
    reactive_power: Attribute | None = None

    # Metadata
    nominal_voltage: Metadata | None = None

    # Relationships
    grid: AssetRelationship | None = None
