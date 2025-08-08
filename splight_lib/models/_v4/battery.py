from splight_lib.models._v4.asset import AssetParams, AssetRelationship
from splight_lib.models._v4.attribute import Attribute
from splight_lib.models._v4.metadata import Metadata
from splight_lib.models.database import SplightDatabaseBaseModel


class Battery(AssetParams, SplightDatabaseBaseModel):
    # Input Attributes
    active_power: Attribute | None = None
    reactive_power: Attribute | None = None
    state_of_charge: Attribute | None = None

    # Computed Attributes
    daily_ideal_revenue: Attribute | None = None
    daily_revenue: Attribute | None = None
    forecasted_state_of_charge_48H: Attribute | None = None
    forecasted_daily_revenue_48H: Attribute | None = None
    forecasted_hourly_revenue_48H: Attribute | None = None
    hourly_revenue: Attribute | None = None
    ideal_state_of_charge: Attribute | None = None
    monthly_cycle_count: Attribute | None = None
    trade_action: Attribute | None = None

    # Metadata
    capacity: Metadata | None = None
    charge_speed: Metadata | None = None
    cycles_per_market: Metadata | None = None
    discharge_speed: Metadata | None = None
    market_opening_time: Metadata | None = None

    # Relationships
    bus: AssetRelationship | None = None
    grid: AssetRelationship | None = None
