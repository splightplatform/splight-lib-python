from pydantic import BaseModel
from typing import Dict


class Deployment(BaseModel):
    id: str
    type: str
    version: str
    external_id: str = None
    status: str = None

class Namespace(BaseModel):
    id: str
    environment: Dict = {}
