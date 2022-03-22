from pydantic import BaseModel
from typing import List, Optional


class Runner(BaseModel):
    id: Optional[str]
    name: str
    description: Optional[str]
    tag_id: str
    algorithm_id: str
    settings: List[dict] = []