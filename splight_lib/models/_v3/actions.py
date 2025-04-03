from datetime import datetime

from splight_lib.models.database import (
    ResourceSummary,
    SplightDatabaseBaseModel,
)


class SetPoint(SplightDatabaseBaseModel):
    id: str | None = None
    name: str
    value: str
    attribute: ResourceSummary


class Action(SplightDatabaseBaseModel):
    id: str | None = None
    name: str
    setpoints: list[SetPoint] = []
    asset: ResourceSummary | None = None
    last_event_timestamp: datetime | None = None
