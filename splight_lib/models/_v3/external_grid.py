from splight_lib.models._v3.asset import AssetParams, AssetRelationship
from splight_lib.models._v3.database_base import SplightDatabaseBaseModel


class ExternalGrid(AssetParams, SplightDatabaseBaseModel):
    bus: AssetRelationship | None = None
    grid: AssetRelationship | None = None
