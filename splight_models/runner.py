from typing import List, Any, Optional
from .base import SplightBaseModel


class Parameter(SplightBaseModel):
    name: str
    type: str = "str"
    required: bool = False
    multiple: bool = False
    value: Any = None


class Runner(SplightBaseModel):
    id: Optional[str]
    name: str
    description: Optional[str]
    version: str  # Pointer to hub component
    parameters: List[Parameter] = []
    readme_url: Optional[str]


class Algorithm(Runner):
    asset_id: str = None
    sub_algorithms: List[Any] = []

    @property
    def collection(self):
        return str(self.id)


class Network(Runner):
    pass


class Connector(Runner):
    pass


class A2ADepencies(SplightBaseModel):
    algorithm: str
    dependency: str
