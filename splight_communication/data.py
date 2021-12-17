from typing import List, Dict
from pydantic import BaseModel


class Variable(BaseModel):
    args: Dict
    path: str = None
    field: str = None
    asset_id: str = None


class Message(BaseModel):
    action: str
    variables: List[Variable]
