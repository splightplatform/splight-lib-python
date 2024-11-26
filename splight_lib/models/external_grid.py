from splight_lib.models import AssetParams, AssetRelationship
from splight_lib.models.database_base import SplightDatabaseBaseModel


class ExternalGrid(AssetParams, SplightDatabaseBaseModel):
    bus: None | AssetRelationship = None
    grid: None | AssetRelationship = None
