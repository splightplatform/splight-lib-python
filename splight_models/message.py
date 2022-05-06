from .base import SplightBaseModel
from typing import List
from .variable import Variable


class Message(SplightBaseModel):
    action: str
    variables: List[Variable]
