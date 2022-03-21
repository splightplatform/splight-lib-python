from pydantic import BaseModel
from typing import List, Optional


class Algorithm(BaseModel):
    id: Optional[str]
    name: str
    description: Optional[str] = None
    version: str
    parameters: List[dict] = []