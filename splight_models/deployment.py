from typing import Dict, List, Optional
from splight_models.base import SplightBaseModel
from splight_models.constants import (
    ComponentSize, DeploymentStatus, LogginLevel, RestartPolicy
)
from splight_models.component import BaseComponent


class Deployment(BaseComponent):
    # run-spec
    id: Optional[str] = None
    component_id: Optional[str] = None
    status: Optional[DeploymentStatus] = None
    status_conditions: Optional[List[Dict]] = None
    container_statuses: Optional[List[Dict]] = None
    restarts: int = 0
    tags: Optional[List[str]] = []

    # Template vars for deployment
    namespace: Optional[str] = None
    component_capacity: ComponentSize = ComponentSize.medium
    log_level: LogginLevel = LogginLevel.debug
    restart_policy: RestartPolicy = RestartPolicy.ALWAYS

    # CLI pre setup
    secrets: Optional[str] = None

    class Config:
        use_enum_values = True

    @property
    def secret_name(self):
        return f"{self.namespace}-secret"

    @property
    def service_name(self):
        return f"service-{self.component_id}"


class DeploymentEvent(SplightBaseModel):
    severity: str
    reason: str
    message: str
    namespace: str
    object_id: str
    object_type: str
