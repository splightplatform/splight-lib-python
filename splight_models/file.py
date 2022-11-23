import os
from typing import Optional, Dict
from .base import SplightBaseModel
import json


class File(SplightBaseModel):
    id: Optional[str] = None
    file: str
    description: Optional[str] = None
    metadata: Dict = {}
    content_type: Optional[str] = None
    url: Optional[str] = None

    def __init__(self, **kwargs):
        file = kwargs.pop('file', None)
        file = file.replace('/', os.sep)
        file = file.replace('\\', os.sep)
        kwargs['file'] = file
        super(File, self).__init__(**kwargs)

    @property
    def name(self):
        return self.file.split(os.sep)[-1]

    def json(self, *args, **kwargs):
        prev_metadata = self.metadata
        self.metadata = json.dumps(self.metadata)
        res = super(File, self).json(*args, **kwargs)
        self.metadata = prev_metadata
        return res
