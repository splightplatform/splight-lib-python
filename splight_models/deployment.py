from pydantic import BaseModel
from typing import Optional


class Deployment(BaseModel):
    id: Optional[str] = None
    type: str
    version: str
    external_id: str = None
    status: str = None
