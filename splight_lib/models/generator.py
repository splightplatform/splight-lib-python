from splight_lib.models import (
    AssetParams,
    AssetRelationship,
    Attribute,
    Metadata,
)
from splight_lib.models.database_base import SplightDatabaseBaseModel


class Generator(AssetParams, SplightDatabaseBaseModel):
    active_power: None | Attribute = None
    daily_emission_avoided: None | Attribute = None
    daily_energy: None | Attribute = None
    monthly_energy: None | Attribute = None
    reactive_power: None | Attribute = None
    co2_coefficient: None | Metadata = None
    bus: None | AssetRelationship = None
    grid: None | AssetRelationship = None
