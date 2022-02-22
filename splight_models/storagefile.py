import os
from typing import Optional
from pydantic import BaseModel


class StorageFile(BaseModel):
    id: Optional[str] = None
    file: str

    @property
    def name(self):
        return self.file.split(os.sep)[-1]
