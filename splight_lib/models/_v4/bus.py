from splight_lib.models._v4.asset import AssetParams, AssetRelationship
from splight_lib.models._v4.attribute import Attribute
from splight_lib.models._v4.metadata import Metadata
from splight_lib.models.database import SplightDatabaseBaseModel


class Bus(AssetParams, SplightDatabaseBaseModel):
    # Input attributes
    active_power: Attribute | None = None
    reactive_power: Attribute | None = None

    # Computed attributes
    energy_price: Attribute | None = None
    energy_price_forecast: Attribute | None = None
    forecasted_temperature_48H: Attribute | None = None
    forecasted_wind_speed_48H: Attribute | None = None
    irradiance: Attribute | None = None
    temperature: Attribute | None = None
    wind_direction: Attribute | None = None
    wind_speed: Attribute | None = None

    # Metadata
    bus_id: Metadata | None = None
    nominal_voltage: Metadata | None = None

    # Relationships
    grid: AssetRelationship | None = None
