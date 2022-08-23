from pydantic import Field
from datetime import datetime, timezone
from typing import Optional
from typing import Optional
from .base import SplightBaseModel
from datetime import datetime


class DatalakeModel(SplightBaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RunnerDatalakeModel(DatalakeModel):
    instance_id: Optional[str] = None
    instance_type: Optional[str] = None

# TODO: Add DatalakeDataFrame class
