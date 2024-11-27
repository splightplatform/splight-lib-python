from splight_lib.models import (
    AssetParams,
    AssetRelationship,
    Attribute,
    Metadata,
)
from splight_lib.models.database_base import SplightDatabaseBaseModel


class Bus(AssetParams, SplightDatabaseBaseModel):
    active_power: Attribute | None = None
    reactive_power: Attribute | None = None
    voltage_pu: Attribute | None = None
    nominal_voltage_kv: Metadata | None = None
    grid: AssetRelationship | None = None
