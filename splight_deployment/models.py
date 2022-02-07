from pydantic import BaseModel
from typing import Optional
from jinja2 import Template


class Deployment(BaseModel):
    id: str
    type: str
    subtype: str
    version: str
    status: str = None
    external_id: str = None


class DeploymentInfo(Deployment):
    name: str
    namespace: str
    service: str
    template: Optional[Template] = None

    class Config:
        arbitrary_types_allowed = True

    @property
    def spec(self):
        if self.template:
            return self.template.render(instance=self)
