from pydantic import Field
from typing import Optional
from datetime import datetime, timezone
from splight_models.base import SplightBaseModel

class DatalakeModel(SplightBaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        validate_assignment = True


class ComponentDatalakeModel(DatalakeModel):
    instance_id: Optional[str] = None
    instance_type: Optional[str] = None

    def dict(self, *args, **kwargs):
        d = super().dict(*args, **kwargs)
        return {
            k: v['id'] if isinstance(v, dict) else v
            for k, v in d.items()
        }
