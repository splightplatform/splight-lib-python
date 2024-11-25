from splight_lib.models import Asset, AssetParams, Attribute, Metadata
from splight_lib.models.database_base import SplightDatabaseBaseModel


class Inverter(AssetParams, SplightDatabaseBaseModel):
    accumulated_energy: Attribute
    active_power: Attribute
    daily_energy: Attribute
    device_status: Attribute
    fault_code_1: Attribute
    frequency: Attribute
    normalized_status_text: Attribute
    raw_daily_energy: Attribute
    status_text: Attribute
    temperature: Attribute
    energy_measurement_type: Metadata
    make: Metadata
    model: Metadata
    serial_number: Metadata
    max_active_power: Metadata
    site: None | Asset
    grid: None | Asset
