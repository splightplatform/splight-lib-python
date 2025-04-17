from splight_lib.models._v4.asset import AssetRelationship
from splight_lib.models._v4.base import AssetParams
from splight_lib.models.database import SplightDatabaseBaseModel


class ExternalGrid(AssetParams, SplightDatabaseBaseModel):
    # Relationships
    bus: AssetRelationship | None = None
    grid: AssetRelationship | None = None
