import json
import os
from typing import Dict, Optional

from pydantic import validator
from splight_lib.models.base import SplightDatabaseBaseModel


class File(SplightDatabaseBaseModel):
    id: Optional[str] = None
    file: str
    description: Optional[str] = None
    metadata: Dict = {}
    content_type: Optional[str] = None
    url: Optional[str] = None
    encrypted: Optional[bool] = False

    @validator("file", pre=True)
    def validate_file(cls, v):
        v = v.replace("/", os.sep)
        v = v.replace("\\", os.sep)
        return v

    @property
    def name(self):
        return self.file.split(os.sep)[-1]

    def download(self):
        file = self._db_client.download(
            resource_name=self.__class__.__name__,
            instance=self.dict(),
            decrypt=self.encrypted,
        )
        return file

    def dict(self, *args, **kwargs):
        res = super().dict(*args, **kwargs)
        res["metadata"] = json.dumps(self.metadata)
        return res

    def json(self, *args, **kwargs):
        prev_metadata = self.metadata
        self.metadata = json.dumps(self.metadata)
        res = super().json(*args, **kwargs)
        self.metadata = prev_metadata
        return res
