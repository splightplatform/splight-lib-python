import json
from typing import Dict, List, Optional

from pydantic import Field, field_validator

from splight_lib.constants import DESCRIPTION_MAX_LENGTH
from splight_lib.models.asset import Asset
from splight_lib.models.base import SplightDatabaseBaseModel
from splight_lib.models.exceptions import ForbiddenOperation


class File(SplightDatabaseBaseModel):
    id: Optional[str] = None
    assets: List[Asset] = []
    file: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = Field(
        default=None, max_length=DESCRIPTION_MAX_LENGTH
    )
    metadata: Dict = {}
    content_type: Optional[str] = None
    parent: Optional[str] = None

    @field_validator("metadata", mode="before")
    def validate_metadata(cls, v):
        return json.loads(v) if isinstance(v, str) else v

    def download(self):
        file = self._db_client.download(
            resource_name=self.__class__.__name__,
            instance=self.model_dump(),
        )
        return file

    def model_dump(self, *args, **kwargs):
        res = super().model_dump(*args, **kwargs)
        if self.metadata:
            res["metadata"] = json.dumps(self.metadata)
        return res

    def model_dump_json(self, *args, **kwargs):
        res = super().model_dump_json(*args, **kwargs)
        if self.metadata:
            prev_metadata = self.metadata
            self.metadata = json.dumps(self.metadata)
            self.metadata = prev_metadata
        return res

    def save(self):
        if self.id:
            raise ForbiddenOperation(
                "File object already exists in database. Can't be updated"
            )
        saved = self._db_client.save(
            self.__class__.__name__, self.model_dump(exclude_none=True)
        )
        if not self.id:
            self.id = saved["id"]
        self.name = saved["name"]
