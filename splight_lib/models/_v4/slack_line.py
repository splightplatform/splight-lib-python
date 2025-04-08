from splight_lib.models._v4.asset import AssetRelationship
from splight_lib.models._v4.base import AssetParams
from splight_lib.models.database import SplightDatabaseBaseModel


class SlackLine(AssetParams, SplightDatabaseBaseModel):
    # Relationships
    bus_from: AssetRelationship | None = None
    bus_to: AssetRelationship | None = None
    grid: AssetRelationship | None = None
