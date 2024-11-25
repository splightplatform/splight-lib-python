from splight_lib.models import Asset, AssetParams, Attribute, Metadata
from splight_lib.models.database_base import SplightDatabaseBaseModel


class Generator(AssetParams, SplightDatabaseBaseModel):
    active_power: Attribute
    daily_emission_avoided: Attribute
    daily_energy: Attribute
    monthly_energy: Attribute
    reactive_power: Attribute
    co2_coefficient: Metadata
    bus: None | Asset
    grid: None | Asset
