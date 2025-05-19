from splight_lib.models._v4.asset import AssetParams, AssetRelationship
from splight_lib.models._v4.attribute import Attribute
from splight_lib.models.database import SplightDatabaseBaseModel


class Load(AssetParams, SplightDatabaseBaseModel):
    # Input attributes
    active_power: Attribute | None = None
    reactive_power: Attribute | None = None
    switch_status: Attribute | None = None

    # Relationships
    grid: AssetRelationship | None = None
    bus: AssetRelationship | None = None
