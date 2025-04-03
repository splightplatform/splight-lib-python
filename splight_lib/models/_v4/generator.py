from splight_lib.models._v4.base import (
    AssetParams,
    AssetRelationship,
    Attribute,
    Metadata,
)
from splight_lib.models.database import SplightDatabaseBaseModel


class Generator(AssetParams, SplightDatabaseBaseModel):
    # Input Attributes
    active_power: Attribute | None = None
    reactive_power: Attribute | None = None
    switch_status: Attribute | None = None
    available_active_power: Attribute | None = None
    frequency: Attribute | None = None
    power_set_point: Attribute | None = None

    # Computed Attributes
    regulation_setpoint: Attribute | None = None
    daily_energy: Attribute | None = None
    monthly_energy: Attribute | None = None
    curtailment: Attribute | None = None
    forecasted_active_power: Attribute | None = None
    forecasted_available_active_power: Attribute | None = None
    forecasted_curtailment: Attribute | None = None
    forecasted_energy: Attribute | None = None
    injection_price: Attribute | None = None
    daily_emissions_avoided: Attribute | None = None
    daily_curtail_power: Attribute | None = None
    daily_curtail_energy: Attribute | None = None
    monthly_curtail_power: Attribute | None = None
    monthly_curtail_energy: Attribute | None = None

    # Metadata
    max_active_power: Metadata | None = None
    co2_intensity_per_kwh: Metadata | None = None
    installed_power: Metadata | None = None

    # Relationships
    bus: AssetRelationship | None = None
    grid: AssetRelationship | None = None
