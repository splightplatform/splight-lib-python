from splight_lib.models import AssetParams, AssetRelationship
from splight_lib.models.database_base import SplightDatabaseBaseModel


class SlackLine(AssetParams, SplightDatabaseBaseModel):
    bus_from: None | AssetRelationship = None
    bus_to: None | AssetRelationship = None
    grid: None | AssetRelationship = None
