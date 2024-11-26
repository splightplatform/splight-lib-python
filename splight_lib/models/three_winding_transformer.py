from splight_lib.models import (
    AssetParams,
    AssetRelationship,
    Attribute,
    Metadata,
)
from splight_lib.models.database_base import SplightDatabaseBaseModel


class ThreeWindingTransformer(AssetParams, SplightDatabaseBaseModel):
    active_power_hv: None | Attribute = None
    active_power_lv: None | Attribute = None
    active_power_mv: None | Attribute = None
    reactive_power_hv: None | Attribute = None
    reactive_power_lv: None | Attribute = None
    reactive_power_mv: None | Attribute = None
    active_power_loss: None | Attribute = None
    reactive_power_loss: None | Attribute = None
    current_hv: None | Attribute = None
    current_lv: None | Attribute = None
    current_mv: None | Attribute = None
    voltage_hv: None | Attribute = None
    voltage_lv: None | Attribute = None
    voltage_mv: None | Attribute = None
    tap_pos: None | Metadata = None
    xn_ohm: None | Metadata = None
    standard_type: None | Metadata = None
    hv_bus: None | AssetRelationship = None
    mv_bus: None | AssetRelationship = None
    lv_bus: None | AssetRelationship = None
    grid: None | AssetRelationship = None
