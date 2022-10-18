from pydantic import Field
from datetime import datetime, timezone
from typing import Optional
from typing import Optional
from .base import SplightBaseModel
from datetime import datetime


class DatalakeModel(SplightBaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        validate_assignment = True


class RunnerDatalakeModel(DatalakeModel):
    instance_id: Optional[str] = None
    instance_type: Optional[str] = None

    def dict(self, *args, **kwargs):
        d = super().dict(*args, **kwargs)
        return {
            k: v['id'] if isinstance(v, dict) else v
            for k, v in d.items()
        }

class IngestionDatalakeModel(DatalakeModel):
    asset: str
    attribute: str
    ingestion_id: str
    type: str
    value: str
