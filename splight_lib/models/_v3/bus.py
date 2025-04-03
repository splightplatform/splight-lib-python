from splight_lib.models._v3.asset import (
    AssetParams,
    AssetRelationship,
    Attribute,
)
from splight_lib.models._v3.metadata import Metadata
from splight_lib.models.database import SplightDatabaseBaseModel


class Bus(AssetParams, SplightDatabaseBaseModel):
    active_power: Attribute | None = None
    reactive_power: Attribute | None = None
    voltage_pu: Attribute | None = None
    nominal_voltage_kv: Metadata | None = None
    grid: AssetRelationship | None = None
