from pydantic import BaseModel
from typing import List, Optional


class Asset(BaseModel):
    id: Optional[str]
    external_id: Optional[str]
    name: str
