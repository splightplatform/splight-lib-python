from splight_lib.models import AssetParams, AssetRelationship
from splight_lib.models.database_base import SplightDatabaseBaseModel


class SlackGenerator(AssetParams, SplightDatabaseBaseModel):
    bus: AssetRelationship | None = None
    grid: AssetRelationship | None = None
