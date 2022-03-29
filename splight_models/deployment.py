from pydantic import BaseModel
from typing import Optional, List
from splight_models.runner import Parameter

class Deployment(BaseModel):
    id: Optional[str] = None
    type: str # eg. ClientConnector, Runner
    external_id: str = None # eg. 1
    name: Optional[str] = None # eg. Forecasting, NetworkManager
    version: str # eg. 0_2
    parameters: List[Parameter] = []
    namespace: Optional[str] = None

    @property
    def hub_identifier(self):
        return f"{self.name}-{self.version}"
