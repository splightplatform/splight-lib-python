from splight_lib.models import Asset, AssetParams, Attribute, Metadata
from splight_lib.models.database_base import SplightDatabaseBaseModel


class Bus(AssetParams, SplightDatabaseBaseModel):
    active_power: Attribute
    reactive_power: Attribute
    voltage_pu: Attribute
    nominal_voltage_kv: Metadata
    grid: None | Asset
