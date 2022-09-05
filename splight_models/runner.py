from typing import List, Any, Optional
from splight_models.base import SplightBaseModel
from splight_models.constants import ComponentSize, RestartPolicy, LogginLevel, RunnerStatus


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
    version: str
    parameters: List[Parameter] = []
    log_level: LogginLevel = LogginLevel.info
    component_capacity: ComponentSize = ComponentSize.small
    restart_policy: RestartPolicy = RestartPolicy.ON_FAILURE
    status: RunnerStatus = RunnerStatus.STOPPED

    @property
    def collection(self):
        return 'default'


class Algorithm(Runner):
    pass

    @property
    def collection(self):
        return str(self.id)


class Network(Runner):
    @property
    def collection(self):
        return 'default'


class Connector(Runner):
    @property
    def collection(self):
        return 'default'
