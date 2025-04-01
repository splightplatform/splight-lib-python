from splight_lib.models._v4.base import AssetParams, AssetRelationship
from splight_lib.models.database_base import SplightDatabaseBaseModel


class ExternalGrid(AssetParams, SplightDatabaseBaseModel):
    # Relationships
    bus: AssetRelationship | None = None
    grid: AssetRelationship | None = None
