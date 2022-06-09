import os
from typing import Optional, List
from .base import SplightBaseModel


class StorageFile(SplightBaseModel):
    id: Optional[str] = None
    file: str
    content_type: Optional[str] = None

    def __init__(self, **kwargs):
        file = kwargs.pop('file', None)
        file = file.replace('/', os.sep)
        file = file.replace('\\', os.sep)
        kwargs['file'] = file
        super(StorageFile, self).__init__(**kwargs)

    @property
    def name(self):
        return self.file.split(os.sep)[-1]
