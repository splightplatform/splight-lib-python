from splight_lib.models import Asset, AssetParams, Attribute, Metadata
from splight_lib.models.database_base import SplightDatabaseBaseModel


class Transformer(AssetParams, SplightDatabaseBaseModel):
    active_power_hv: Attribute
    active_power_lv: Attribute
    reactive_power_hv: Attribute
    reactive_power_lv: Attribute
    active_power_loss: Attribute
    reactive_power_loss: Attribute
    current_hv: Attribute
    current_lv: Attribute
    voltage_hv: Attribute
    voltage_lv: Attribute
    tap_pos: Metadata
    xn_ohm: Metadata
    standard_type: Metadata
    capacitance: Metadata
    conductance: Metadata
    maximum_allowed_current: Metadata
    maximum_allowed_power: Metadata
    reactance: Metadata
    resistance: Metadata
    safety_margin_for_power: Metadata
    hv_bus: None | Asset
    lv_bus: None | Asset
    grid: None | Asset