from splight_lib.models import AssetParams, AssetRelationship
from splight_lib.models.database_base import SplightDatabaseBaseModel


class SlackLine(AssetParams, SplightDatabaseBaseModel):
    bus_from: AssetRelationship | None = None
    bus_to: AssetRelationship | None = None
    grid: AssetRelationship | None = None
