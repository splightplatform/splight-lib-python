import os
from typing import Optional, List
from pydantic import BaseModel


class StorageFile(BaseModel):
    id: Optional[str] = None
    file: str

    def __init__(self, **kwargs):
        file = kwargs.pop('file', None)
        file = file.replace('/', os.sep)
        file = file.replace('\\', os.sep)
        kwargs['file'] = file
        super(StorageFile, self).__init__(**kwargs)

    @property
    def name(self):
        return self.file.split(os.sep)[-1]


# TODO: Remove this
class StorageDirectory(BaseModel):
    id: Optional[str] = None
    dir: str
    files: List[StorageFile] = list()

    @property
    def name(self):
        return self.dir.split(os.sep)[-1]
