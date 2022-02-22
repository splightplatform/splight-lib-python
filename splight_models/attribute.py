from pydantic import BaseModel
from typing import Optional


class Attribute(BaseModel):
    id: Optional[str]
    name: str
