from typing import List, Any, Optional
from pydantic import BaseModel


class Parameter(BaseModel):
    name: str
    type: str = "str"
    required: bool = False
    value: Any = None


class Runner(BaseModel):
    id: Optional[str]
    name: str
    description: Optional[str]
    tag_id: str
    version: str
    parameters: List[Parameter] =   []
