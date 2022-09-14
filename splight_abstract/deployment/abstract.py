import json
from abc import abstractmethod
from pydantic import BaseModel
from typing import Dict, Type, List, Optional
from splight_abstract.client import AbstractClient, QuerySet
from splight_models.deployment import DeploymentEvent
from remote_splight_lib.auth import HmacSignature


class AbstractDeploymentClient(AbstractClient):
    @abstractmethod
    def save(self, instance: BaseModel) -> BaseModel:
        pass

    def get(self, *args, **kwargs) -> QuerySet:
        return QuerySet(self, *args, **kwargs)

    @abstractmethod
    def _get(self, resource_type: Type, id: str = '', first=False, limit_: int = -1, skip_: int = 0, **kwargs) -> List[BaseModel]:
        pass

    @abstractmethod
    def delete(self, resource_type: Type, id: str) -> None:
        pass

    def get_deployment_logs(self, id: str, limit: Optional[int] = None, since: Optional[str] = None) -> List[str]:
        pass

    @staticmethod
    def construct_event(payload: bytes, signature: str, secret: str) -> DeploymentEvent:
        HmacSignature.verify_header(
            payload, signature, secret
        )
        event = json.loads(payload)
        return DeploymentEvent.parse_obj(event)
