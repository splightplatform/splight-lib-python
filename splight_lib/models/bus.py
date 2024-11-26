from splight_lib.models import (
    AssetParams,
    AssetRelationship,
    Attribute,
    Metadata,
)
from splight_lib.models.database_base import SplightDatabaseBaseModel


class Bus(AssetParams, SplightDatabaseBaseModel):
    active_power: None | Attribute = None
    reactive_power: None | Attribute = None
    voltage_pu: None | Attribute = None
    nominal_voltage_kv: None | Metadata = None
    grid: None | AssetRelationship = None
