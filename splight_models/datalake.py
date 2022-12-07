from pydantic import Field
from typing import Optional
from datetime import datetime, timezone
from splight_models.base import SplightBaseModel


class DatalakeModel(SplightBaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    instance_id: Optional[str] = None
    instance_type: Optional[str] = None

    class Config:
        # pydantic
        validate_assignment = True

    class Meta:
        collection_name = "DatalakeModel"

    class SpecFields:
        # Fields to reconstruct Spec .fields
        pass

    def dict(self, *args, **kwargs):
        d = super().dict(*args, **kwargs)
        return {
            k: v['id'] if isinstance(v, dict) and 'id' in v.keys() else v
            for k, v in d.items()
        }

    def json(self, *args, **kwargs):
        restore = {}

        for k in self.__class__.__fields__.keys():
            v = getattr(self, k)
            if hasattr(v, "id"):
                restore[k] = v.id
                setattr(self, k, v.id)

        res = super().json(*args, **kwargs)

        for k, v in restore.items():
            setattr(self, k, v)

        return res
