from typing import Dict, List, Optional
from splight_models.base import SplightBaseModel
from splight_models.constants import ComponentSize, ComponentType, DeploymentStatus, LogginLevel, RestartPolicy
from splight_models.component import BaseComponent, Endpoint


class Deployment(BaseComponent):
    # run-spec
    id: Optional[str] = None
    type: ComponentType = ComponentType.COMPONENT
    component_id: Optional[str] = None
    status: Optional[DeploymentStatus] = None
    status_conditions: Optional[List[Dict]] = None
    container_statuses: Optional[List[Dict]] = None
    tags: Optional[List[str]] = []

    # Template vars for deployment
    namespace: Optional[str] = None
    component_capacity: ComponentSize = ComponentSize.medium
    log_level: LogginLevel = LogginLevel.debug
    restart_policy: RestartPolicy = RestartPolicy.ALWAYS

    # CLI pre setup
    secrets: Optional[str] = None

    # TODO: Remove the following attributes
    access_id: Optional[str] = None
    secret_key: Optional[str] = None
    hub_api_host: Optional[str] = None
    api_host: Optional[str] = None
    endpoints: Optional[List[Endpoint]] = None
    service_name: Optional[str] = None

    class Config:
        use_enum_values = True

    @property
    def deployment_name(self):
        # TODO remove this. we are no longeer using deployments.
        id = str(self.id).lower()
        type_id = str(self.type).lower()
        return f"deployment-{id}"


class DeploymentEvent(SplightBaseModel):
    severity: str
    reason: str
    message: str
    namespace: str
    object_id: str
    object_type: str
