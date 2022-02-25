from pydantic import BaseModel
from typing import Optional


class Tag(BaseModel):
    id: Optional[str]
    name: str
    description: Optional[str]
