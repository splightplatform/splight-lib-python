from splight_lib.models import AssetParams, AssetRelationship, Attribute
from splight_lib.models.database_base import SplightDatabaseBaseModel


class SlackGenerator(AssetParams, SplightDatabaseBaseModel):
    switch_status: Attribute | None = None
    bus: AssetRelationship | None = None
    grid: AssetRelationship | None = None
