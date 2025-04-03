from splight_lib.models._v3.asset import (
    AssetParams,
    AssetRelationship,
    Attribute,
)
from splight_lib.models.database import SplightDatabaseBaseModel


class Load(AssetParams, SplightDatabaseBaseModel):
    active_power: Attribute | None = None
    reactive_power: Attribute | None = None
    switch_status: Attribute | None = None
    bus: AssetRelationship | None = None
    grid: AssetRelationship | None = None
