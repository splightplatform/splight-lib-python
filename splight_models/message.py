from pydantic import BaseModel
from typing import List
from .variable import Variable


class Message(BaseModel):
    action: str
    variables: List[Variable]
