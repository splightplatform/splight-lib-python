from splight_lib.models._v3.asset import (
    AssetParams,
    AssetRelationship,
    Attribute,
)
from splight_lib.models._v3.metadata import Metadata
from splight_lib.models.database import SplightDatabaseBaseModel


class Generator(AssetParams, SplightDatabaseBaseModel):
    active_power: Attribute | None = None
    daily_emission_avoided: Attribute | None = None
    daily_energy: Attribute | None = None
    monthly_energy: Attribute | None = None
    reactive_power: Attribute | None = None
    switch_status: Attribute | None = None
    co2_coefficient: Metadata | None = None
    bus: AssetRelationship | None = None
    grid: AssetRelationship | None = None
