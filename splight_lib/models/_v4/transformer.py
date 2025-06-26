from splight_lib.models._v4.asset import AssetParams, AssetRelationship
from splight_lib.models._v4.attribute import Attribute
from splight_lib.models._v4.metadata import Metadata
from splight_lib.models.database import SplightDatabaseBaseModel


class Transformer(AssetParams, SplightDatabaseBaseModel):
    # Input attributes
    active_power_hv: Attribute | None = None
    active_power_loss: Attribute | None = None
    active_power_lv: Attribute | None = None
    contingency: Attribute | None = None
    reactive_power_hv: Attribute | None = None
    reactive_power_loss: Attribute | None = None
    reactive_power_lv: Attribute | None = None
    switch_status_hv: Attribute | None = None
    switch_status_lv: Attribute | None = None
    voltage_hv: Attribute | None = None
    voltage_lv: Attribute | None = None

    # Computed attributes
    contingency_solving_time: Attribute | None = None
    current_hv: Attribute | None = None
    current_lv: Attribute | None = None
    generators_output_vector: Attribute | None = None
    historical_generators_output_vector: Attribute | None = None
    objective_power: Attribute | None = None

    # Metadata
    capacitance: Metadata | None = None
    conductance: Metadata | None = None
    maximum_allowed_current: Metadata | None = None
    maximum_allowed_power: Metadata | None = None
    reactance: Metadata | None = None
    resistance: Metadata | None = None
    safety_margin_for_power: Metadata | None = None
    standard_type: Metadata | None = None
    tap_pos: Metadata | None = None
    xn: Metadata | None = None

    # Relationships
    grid: AssetRelationship | None = None
    hv_bus: AssetRelationship | None = None
    lv_bus: AssetRelationship | None = None
