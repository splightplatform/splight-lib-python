from splight_lib.models import AssetParams, AssetRelationship, Attribute
from splight_lib.models.database_base import SplightDatabaseBaseModel
from splight_lib.models.metadata import Metadata


class Line(AssetParams, SplightDatabaseBaseModel):
    active_power: Attribute | None = None
    reactive_power: Attribute | None = None
    ampacity: Attribute | None = None
    max_temperature: Attribute | None = None
    energy: Attribute | None = None
    current_r: Attribute | None = None
    current_s: Attribute | None = None
    current_t: Attribute | None = None
    current: Attribute | None = None
    voltage_rs: Attribute | None = None
    voltage_st: Attribute | None = None
    voltage_tr: Attribute | None = None
    active_power_end: Attribute | None = None
    contingency: Attribute | None = None
    switch_status_start: Attribute | None = None
    switch_status_end: Attribute | None = None
    absorptivity: Metadata | None = None
    atmosphere: Metadata | None = None
    diameter: Metadata | None = None
    emissivity: Metadata | None = None
    maximum_allowed_temperature: Metadata | None = None
    number_of_conductors: Metadata | None = None
    reactance: Metadata | None = None
    reference_resistance: Metadata | None = None
    resistance: Metadata | None = None
    susceptance: Metadata | None = None
    temperature_coeff_resistance: Metadata | None = None
    maximum_allowed_temperature_lte: Metadata | None = None
    maximum_allowed_temperature_ste: Metadata | None = None
    length: Metadata | None = None
    conductance: Metadata | None = None
    capacitance: Metadata | None = None
    maximum_allowed_current: Metadata | None = None
    maximum_allowed_power: Metadata | None = None
    safety_margin_for_power: Metadata | None = None
    specific_heat: Metadata | None = None
    conductor_mass: Metadata | None = None
    thermal_elongation_coef: Metadata | None = None
    bus_from: AssetRelationship | None = None
    bus_to: AssetRelationship | None = None
    grid: AssetRelationship | None = None
