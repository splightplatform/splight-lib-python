import json
import os
from typing import Dict, Optional

from pydantic import Field, field_validator

from splight_lib.constants import DESCRIPTION_MAX_LENGTH
from splight_lib.models.base import SplightDatabaseBaseModel


class File(SplightDatabaseBaseModel):
    id: Optional[str] = None
    file: str
    description: Optional[str] = Field(
        default=None, max_length=DESCRIPTION_MAX_LENGTH
    )
    metadata: Dict = {}
    content_type: Optional[str] = None
    url: Optional[str] = None

    @field_validator("file", mode="after")
    def validate_file(cls, v):
        v = v.replace("/", os.sep)
        v = v.replace("\\", os.sep)
        return v

    @field_validator("metadata", mode="before")
    def validate_metadata(cls, v):
        return json.loads(v) if isinstance(v, str) else v

    @property
    def name(self):
        return self.file.split(os.sep)[-1]

    def download(self):
        file = self._db_client.download(
            resource_name=self.__class__.__name__,
            instance=self.model_dump(),
        )
        return file

    def model_dump(self, *args, **kwargs):
        res = super().model_dump(*args, **kwargs)
        res["metadata"] = json.dumps(self.metadata)
        return res

    def model_dump_json(self, *args, **kwargs):
        prev_metadata = self.metadata
        self.metadata = json.dumps(self.metadata)
        res = super().model_dump_json(*args, **kwargs)
        self.metadata = prev_metadata
        return res
