from .base import SplightBaseModel
from typing import Optional, Dict
from pydantic import validator
import json
import os


class File(SplightBaseModel):
    id: Optional[str] = None
    file: str
    description: Optional[str] = None
    metadata: Dict = {}
    content_type: Optional[str] = None
    url: Optional[str] = None
    encrypted: Optional[bool] = False

    @validator("file", pre=True)
    def validate_file(cls, v):
        v = v.replace('/', os.sep)
        v = v.replace('\\', os.sep)
        return v

    @property
    def name(self):
        return self.file.split(os.sep)[-1]

    def json(self, *args, **kwargs):
        prev_metadata = self.metadata
        self.metadata = json.dumps(self.metadata)
        res = super(File, self).json(*args, **kwargs)
        self.metadata = prev_metadata
        return res
