import json

from pydantic import field_validator

from splight_lib.models.database import SplightDatabaseBaseModel


class Folder(SplightDatabaseBaseModel):
    id: str | None = None
    name: str | None = None
    description: str | None = None
    metadata: dict = {}
    parent: str | None = None

    @field_validator("metadata", mode="before")
    def validate_metadata(cls, v):
        return json.loads(v) if isinstance(v, str) else v

    def model_dump(self, *args, **kwargs):
        res = super().model_dump(*args, **kwargs)
        if self.metadata:
            res["metadata"] = json.dumps(self.metadata)
        return res
