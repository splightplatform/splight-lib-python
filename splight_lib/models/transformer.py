from splight_lib.models import (
    AssetParams,
    AssetRelationship,
    Attribute,
    Metadata,
)
from splight_lib.models.database_base import SplightDatabaseBaseModel


class Transformer(AssetParams, SplightDatabaseBaseModel):
    active_power_hv: Attribute | None = None
    active_power_lv: Attribute | None = None
    reactive_power_hv: Attribute | None = None
    reactive_power_lv: Attribute | None = None
    active_power_loss: Attribute | None = None
    reactive_power_loss: Attribute | None = None
    current_hv: Attribute | None = None
    current_lv: Attribute | None = None
    voltage_hv: Attribute | None = None
    voltage_lv: Attribute | None = None
    contingency: Attribute | None = None
    switch_status_lv: Attribute | None = None
    switch_status_hv: Attribute | None = None
    tap_pos: Metadata | None = None
    xn_ohm: Metadata | None = None
    standard_type: Metadata | None = None
    capacitance: Metadata | None = None
    conductance: Metadata | None = None
    maximum_allowed_current: Metadata | None = None
    maximum_allowed_power: Metadata | None = None
    reactance: Metadata | None = None
    resistance: Metadata | None = None
    safety_margin_for_power: Metadata | None = None
    hv_bus: AssetRelationship | None = None
    lv_bus: AssetRelationship | None = None
    grid: AssetRelationship | None = None
