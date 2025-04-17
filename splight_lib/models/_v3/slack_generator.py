from splight_lib.models._v3.asset import (
    AssetParams,
    AssetRelationship,
    Attribute,
)
from splight_lib.models.database import SplightDatabaseBaseModel


class SlackGenerator(AssetParams, SplightDatabaseBaseModel):
    switch_status: Attribute | None = None
    bus: AssetRelationship | None = None
    grid: AssetRelationship | None = None
