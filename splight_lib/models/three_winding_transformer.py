from splight_lib.models import Asset, AssetParams, Attribute, Metadata
from splight_lib.models.database_base import SplightDatabaseBaseModel


class ThreeWindingTransformer(AssetParams, SplightDatabaseBaseModel):
    active_power_hv: Attribute
    active_power_lv: Attribute
    active_power_mv: Attribute
    reactive_power_hv: Attribute
    reactive_power_lv: Attribute
    reactive_power_mv: Attribute
    active_power_loss: Attribute
    reactive_power_loss: Attribute
    current_hv: Attribute
    current_lv: Attribute
    current_mv: Attribute
    voltage_hv: Attribute
    voltage_lv: Attribute
    voltage_mv: Attribute
    tap_pos: Metadata
    xn_ohm: Metadata
    standard_type: Metadata
    hv_bus: None | Asset
    mv_bus: None | Asset
    lv_bus: None | Asset
    grid: None | Asset