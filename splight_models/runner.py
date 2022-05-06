from typing import List, Any, Optional
from .base import SplightBaseModel


class Parameter(SplightBaseModel):
    name: str
    type: str = "str"
    required: bool = False
    value: Any = None


class Runner(SplightBaseModel):
    id: Optional[str]
    name: str
    description: Optional[str]
    version: str
    parameters: List[Parameter] =   []


class Algorithm(Runner):
    pass


class Network(Runner):
    pass


class Connector(Runner):
    pass
