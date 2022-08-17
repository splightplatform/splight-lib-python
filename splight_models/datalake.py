from pydantic import Field
from datetime import datetime, timezone
from typing import Optional
from typing import Optional
from .base import SplightBaseModel
from datetime import datetime


class DatalakeModel(SplightBaseModel):
    instance_id: Optional[str] = None
    instance_type: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# TODO: Add DatalakeDataFrame class
