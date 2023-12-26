import json
import os
from typing import Dict, List, Optional

from pydantic import Field, field_validator, model_validator
from pysher.pusher import hashlib

from splight_lib.constants import DESCRIPTION_MAX_LENGTH
from splight_lib.models.asset import Asset
from splight_lib.models.base import SplightDatabaseBaseModel


class File(SplightDatabaseBaseModel):
    id: Optional[str] = None
    assets: List[Asset] = []
    file: str
    description: Optional[str] = Field(
        default=None, max_length=DESCRIPTION_MAX_LENGTH
    )
    metadata: Dict = {}
    content_type: Optional[str] = None
    url: Optional[str] = None
    checksum: Optional[str] = None

    @model_validator(mode="after")
    def validate_file(self):
        self.file = self.file.replace("/", os.sep)
        self.file = self.file.replace("\\", os.sep)

        # Compute the checksum if missing
        if self.checksum is None:
            hasher = hashlib.md5()
            with open(self.file, "rb") as file:
                # Read in chunks of 8KiB for large files
                while chunk := file.read(8192):
                    hasher.update(chunk)
            self.checksum = hasher.hexdigest()

        return self

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
