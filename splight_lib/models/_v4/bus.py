from splight_lib.models._v4.base import (
    AssetParams,
    AssetRelationship,
    Attribute,
    Metadata,
)
from splight_lib.models.database import SplightDatabaseBaseModel


class Bus(AssetParams, SplightDatabaseBaseModel):
    # Input attributes
    active_power: Attribute | None = None
    reactive_power: Attribute | None = None

    # Metadata
    nominal_voltage: Metadata | None = None

    # Relationships
    grid: AssetRelationship | None = None
