from typing import List, Any, Optional
from pydantic import BaseModel


class Parameter(BaseModel):
    name: str
    type: str = "str"
    required: bool = False
    value: Any = None


class Algorithm(BaseModel):
    id: Optional[str]
    name: str
    description: Optional[str]
    version: str
    parameters: List[Parameter]


class Runner(BaseModel):
    id: Optional[str]
    name: str
    description: Optional[str]
    tag_id: str
    algorithm_id: str
    parameters: List[Parameter]
