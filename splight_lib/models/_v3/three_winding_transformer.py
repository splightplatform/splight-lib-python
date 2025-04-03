from splight_lib.models._v3.asset import (
    AssetParams,
    AssetRelationship,
    Attribute,
    Metadata,
)
from splight_lib.models.database import SplightDatabaseBaseModel


class ThreeWindingTransformer(AssetParams, SplightDatabaseBaseModel):
    active_power_hv: Attribute | None = None
    active_power_lv: Attribute | None = None
    active_power_mv: Attribute | None = None
    reactive_power_hv: Attribute | None = None
    reactive_power_lv: Attribute | None = None
    reactive_power_mv: Attribute | None = None
    active_power_loss: Attribute | None = None
    reactive_power_loss: Attribute | None = None
    current_hv: Attribute | None = None
    current_lv: Attribute | None = None
    current_mv: Attribute | None = None
    voltage_hv: Attribute | None = None
    voltage_lv: Attribute | None = None
    voltage_mv: Attribute | None = None
    switch_status_lv: Attribute | None = None
    switch_status_mv: Attribute | None = None
    switch_status_hv: Attribute | None = None
    tap_pos: Metadata | None = None
    xn_ohm: Metadata | None = None
    standard_type: Metadata | None = None
    hv_bus: AssetRelationship | None = None
    mv_bus: AssetRelationship | None = None
    lv_bus: AssetRelationship | None = None
    grid: AssetRelationship | None = None
