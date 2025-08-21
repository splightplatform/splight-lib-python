from splight_lib.models._v4.asset import AssetParams, AssetRelationship
from splight_lib.models._v4.attribute import Attribute
from splight_lib.models._v4.metadata import Metadata
from splight_lib.models.database import SplightDatabaseBaseModel


class Line(AssetParams, SplightDatabaseBaseModel):
    # Input attributes
    active_power_end: Attribute | None = None
    active_power_start: Attribute | None = None
    contingency: Attribute | None = None
    current_r_end: Attribute | None = None
    current_r_start: Attribute | None = None
    current_s_end: Attribute | None = None
    current_s_start: Attribute | None = None
    current_t_end: Attribute | None = None
    current_t_start: Attribute | None = None
    frequency: Attribute | None = None
    reactive_power_end: Attribute | None = None
    reactive_power_start: Attribute | None = None
    switch_status_end: Attribute | None = None
    switch_status_start: Attribute | None = None
    voltage_end: Attribute | None = None
    voltage_start: Attribute | None = None

    # Computed attributes
    ampacity_aar: Attribute | None = None
    ampacity_aar_lte: Attribute | None = None
    ampacity_aar_ste: Attribute | None = None
    ampacity_dlr: Attribute | None = None
    ampacity_dlr_lte: Attribute | None = None
    ampacity_dlr_ste: Attribute | None = None
    contingency_solving_time: Attribute | None = None
    dlr_irradiance: Attribute | None = None
    dlr_temperature: Attribute | None = None
    dlr_wind_direction: Attribute | None = None
    dlr_wind_speed: Attribute | None = None
    forecasted_ampacity_aar_240H: Attribute | None = None
    forecasted_ampacity_aar_48H: Attribute | None = None
    forecasted_ampacity_aar_72H: Attribute | None = None
    forecasted_ampacity_dlr_240H: Attribute | None = None
    forecasted_ampacity_dlr_48H: Attribute | None = None
    forecasted_ampacity_dlr_72H: Attribute | None = None
    generators_vector: Attribute | None = None
    historical_segment_aar_vector: Attribute | None = None
    historical_segment_dlr_vector: Attribute | None = None
    historical_generators_vector: Attribute | None = None
    loads_vector: Attribute | None = None
    historical_loads_vector: Attribute | None = None
    max_conductor_temp: Attribute | None = None
    max_temperature_segment_dlr: Attribute | None = None
    min_amp_segment_aar: Attribute | None = None
    min_amp_segment_aar_lte: Attribute | None = None
    min_amp_segment_aar_ste: Attribute | None = None
    min_amp_segment_dlr: Attribute | None = None
    min_amp_segment_dlr_lte: Attribute | None = None
    min_amp_segment_dlr_ste: Attribute | None = None
    objective_power: Attribute | None = None
    sag: Attribute | None = None
    sag_rating: Attribute | None = None

    # Metadata
    absorptivity: Metadata | None = None
    atmosphere: Metadata | None = None
    capacitance: Metadata | None = None
    conductance: Metadata | None = None
    conductor_mass: Metadata | None = None
    diameter: Metadata | None = None
    emissivity: Metadata | None = None
    length: Metadata | None = None
    maximum_allowed_current: Metadata | None = None
    maximum_allowed_power: Metadata | None = None
    maximum_allowed_temperature: Metadata | None = None
    maximum_allowed_temperature_lte: Metadata | None = None
    maximum_allowed_temperature_ste: Metadata | None = None
    monitored_line: Metadata | None = None
    n_1_capacity: Metadata | None = None
    number_of_conductors: Metadata | None = None
    reactance: Metadata | None = None
    reference_resistance: Metadata | None = None
    resistance: Metadata | None = None
    safety_margin_for_power: Metadata | None = None
    specific_heat: Metadata | None = None
    static_ampacity: Metadata | None = None
    static_ampacity_lte: Metadata | None = None
    static_ampacity_ste: Metadata | None = None
    static_power_ste: Metadata | None = None
    susceptance: Metadata | None = None
    temperature_coeff_resistance: Metadata | None = None
    thermal_elongation_coeff: Metadata | None = None

    # Relationships
    bus_from: AssetRelationship | None = None
    bus_to: AssetRelationship | None = None
    grid: AssetRelationship | None = None
