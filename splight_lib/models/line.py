from splight_lib.models import (
    AssetParams,
    AssetRelationship,
    Attribute,
    Metadata,
)
from splight_lib.models.database_base import SplightDatabaseBaseModel


class Line(AssetParams, SplightDatabaseBaseModel):
    active_power: None | Attribute = None
    reactive_power: None | Attribute = None
    ampacity: None | Attribute = None
    max_temperature: None | Attribute = None
    energy: None | Attribute = None
    current_r: None | Attribute = None
    current_s: None | Attribute = None
    current_t: None | Attribute = None
    current: None | Attribute = None
    voltage_rs: None | Attribute = None
    voltage_st: None | Attribute = None
    voltage_tr: None | Attribute = None
    active_power_end: None | Attribute = None
    contingency: None | Attribute = None
    absorptivity: None | Metadata = None
    atmosphere: None | Metadata = None
    diameter: None | Metadata = None
    emissivity: None | Metadata = None
    maximum_allowed_temperature: None | Metadata = None
    number_of_conductors: None | Metadata = None
    reactance: None | Metadata = None
    reference_resistance: None | Metadata = None
    resistance: None | Metadata = None
    susceptance: None | Metadata = None
    temperature_coeff_resistance: None | Metadata = None
    maximum_allowed_temperature_lte: None | Metadata = None
    maximum_allowed_temperature_ste: None | Metadata = None
    length: None | Metadata = None
    conductance: None | Metadata = None
    capacitance: None | Metadata = None
    maximum_allowed_current: None | Metadata = None
    maximum_allowed_power: None | Metadata = None
    safety_margin_for_power: None | Metadata = None
    specific_heat: None | Metadata = None
    conductor_mass: None | Metadata = None
    thermal_elongation_coef: None | Metadata = None
    bus_from: None | AssetRelationship = None
    bus_to: None | AssetRelationship = None
    grid: None | AssetRelationship = None
