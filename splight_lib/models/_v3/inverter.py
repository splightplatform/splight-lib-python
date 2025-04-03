from splight_lib.models._v3.asset import (
    AssetParams,
    AssetRelationship,
    Attribute,
)
from splight_lib.models._v3.metadata import Metadata
from splight_lib.models.database import SplightDatabaseBaseModel


class Inverter(AssetParams, SplightDatabaseBaseModel):
    accumulated_energy: Attribute | None = None
    active_power: Attribute | None = None
    daily_energy: Attribute | None = None
    device_status: Attribute | None = None
    fault_code_1: Attribute | None = None
    frequency: Attribute | None = None
    normalized_status_text: Attribute | None = None
    raw_daily_energy: Attribute | None = None
    status_text: Attribute | None = None
    temperature: Attribute | None = None
    switch_status: Attribute | None = None
    energy_measurement_type: Metadata | None = None
    make: Metadata | None = None
    model: Metadata | None = None
    serial_number: Metadata | None = None
    max_active_power: Metadata | None = None
    site: AssetRelationship | None = None
    grid: AssetRelationship | None = None
