import uuid
from typing import List, Optional, Type

from pydantic import BaseModel

from splight_abstract import (
    AbstractDeploymentClient,
    validate_instance_type,
    validate_resource_type,
)
from splight_lib import logging
from splight_models import Deployment, Namespace

logger = logging.getLogger()


class FakeDeploymentClient(AbstractDeploymentClient):
    namespace = "default"
    deployments = {}
    valid_classes = [Deployment]

    def _get_deployment(self, id: str = "") -> List[Deployment]:
        logger.info("[FAKED] Retrieving fake deployment")
        if id:
            return [
                value for key, value in self.deployments.items() if key == id
            ]
        else:
            return [value for _, value in self.deployments.items()]

    @validate_resource_type
    def _get(
        self,
        resource_type: Type,
        first: bool = False,
        id: str = "",
        limit_: int = -1,
        skip_: int = 0,
        **kwargs,
    ) -> List[BaseModel]:
        if resource_type == Deployment:
            queryset = self._get_deployment(id=id)

        kwargs = self._validated_kwargs(resource_type, **kwargs)
        queryset = self._filter(queryset, **kwargs)
        if limit_ != -1:
            queryset = queryset[skip_:skip_ + limit_]

        if first:
            return queryset[0] if queryset else None
        return queryset

    def _list(self, **kwargs):
        queryset = self._get_deployment()
        return queryset

    def save(self, instance: BaseModel) -> BaseModel:
        raise NotImplementedError

    def delete(self, resource_type: Type, id: str) -> None:
        raise NotImplementedError

    def get_deployment_logs(self, id: str, limit: Optional[int] = None, since: Optional[str] = None, previous: bool = False) -> List[str]:
        raise NotImplementedError

    def get_capacity_options(self):
        raise NotImplementedError