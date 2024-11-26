from splight_lib.models import (
    AssetParams,
    AssetRelationship,
    Attribute,
    Metadata,
)
from splight_lib.models.database_base import SplightDatabaseBaseModel


class Inverter(AssetParams, SplightDatabaseBaseModel):
    accumulated_energy: None | Attribute = None
    active_power: None | Attribute = None
    daily_energy: None | Attribute = None
    device_status: None | Attribute = None
    fault_code_1: None | Attribute = None
    frequency: None | Attribute = None
    normalized_status_text: None | Attribute = None
    raw_daily_energy: None | Attribute = None
    status_text: None | Attribute = None
    temperature: None | Attribute = None
    energy_measurement_type: None | Metadata = None
    make: None | Metadata = None
    model: None | Metadata = None
    serial_number: None | Metadata = None
    max_active_power: None | Metadata = None
    site: None | AssetRelationship = None
    grid: None | AssetRelationship = None
