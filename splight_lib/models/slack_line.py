from splight_lib.models import AssetParams, AssetRelationship, Attribute
from splight_lib.models.database_base import SplightDatabaseBaseModel


class SlackLine(AssetParams, SplightDatabaseBaseModel):
    switch_status_start: Attribute | None = None
    switch_status_end: Attribute | None = None
    bus_from: AssetRelationship | None = None
    bus_to: AssetRelationship | None = None
    grid: AssetRelationship | None = None
