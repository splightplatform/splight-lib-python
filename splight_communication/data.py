from pydantic import BaseModel
from typing import List, Dict, Union, Callable


class Variable(BaseModel):
    args: Dict
    path: str = None
    field: str = None
    asset_id: str = None


class Message(BaseModel):
    action: str
    variables: List[Variable]


Value = Union[int, float, str, bool]
