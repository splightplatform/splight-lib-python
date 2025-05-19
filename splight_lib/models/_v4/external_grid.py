from splight_lib.models._v4.asset import AssetParams, AssetRelationship
from splight_lib.models.database import SplightDatabaseBaseModel


class ExternalGrid(AssetParams, SplightDatabaseBaseModel):
    # Relationships
    bus: AssetRelationship | None = None
    grid: AssetRelationship | None = None
