from splight_lib.models import Asset, AssetParams, Attribute, Metadata
from splight_lib.models.database_base import SplightDatabaseBaseModel


class Line(AssetParams, SplightDatabaseBaseModel):
    active_power: Attribute
    reactive_power: Attribute
    ampacity: Attribute
    max_temperature: Attribute
    energy: Attribute
    current_r: Attribute
    current_s: Attribute
    current_t: Attribute
    current: Attribute
    voltage_rs: Attribute
    voltage_st: Attribute
    voltage_tr: Attribute
    active_power_end: Attribute
    contingency: Attribute
    absorptivity: Metadata
    atmosphere: Metadata
    diameter: Metadata
    emissivity: Metadata
    maximum_allowed_temperature: Metadata
    number_of_conductors: Metadata
    reactance: Metadata
    reference_resistance: Metadata
    resistance: Metadata
    susceptance: Metadata
    temperature_coeff_resistance: Metadata
    maximum_allowed_temperature_lte: Metadata
    maximum_allowed_temperature_ste: Metadata
    length: Metadata
    conductance: Metadata
    capacitance: Metadata
    maximum_allowed_current: Metadata
    maximum_allowed_power: Metadata
    safety_margin_for_power: Metadata
    specific_heat: Metadata
    conductor_mass: Metadata
    thermal_elongation_coef: Metadata
    bus_from: None | Asset
    bus_to: None | Asset
    grid: None | Asset



