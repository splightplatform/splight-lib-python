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
    namespaces = {}
    valid_classes = [Deployment, Namespace]

    def _create_deployment(self, instance: Deployment) -> Deployment:
        logger.info("[FAKED] Applying fake deployment")
        logger.info(instance.dict())
        count = str(uuid.uuid4())
        self.deployments[count] = instance
        instance.id = count
        return instance

    def _get_deployment(self, id: str = "") -> List[Deployment]:
        logger.info("[FAKED] Retrieving fake deployment")
        if id:
            return [
                value for key, value in self.deployments.items() if key == id
            ]
        else:
            return [value for _, value in self.deployments.items()]

    def _delete_deployment(self, id: str) -> None:
        logger.info("[FAKED] Deleting fake deployment")
        try:
            del self.deployments[id]
        except KeyError:
            logger.warning(f"[FAKED] Deployment not present {id}")

    def _create_namespace(self, instance: Namespace) -> Namespace:
        logger.info("[FAKED] Applying fake namespace")
        count = len(self.namespaces)
        self.namespaces[count] = instance
        instance.id = count
        return instance

    def _get_namespace(self, id: str = "") -> List[Namespace]:
        logger.info("[FAKED] Retrieving fake deployment")
        if id:
            return [
                value for key, value in self.deployments.items() if key == id
            ]
        else:
            return [value for _, value in self.deployments.items()]

    def _delete_namespace(self, id: str) -> None:
        logger.info("[FAKED] Deleting fake deployment")
        try:
            del self.namespaces[id]
        except KeyError:
            logger.warning(f"[FAKED] Deployment not present {id}")

    @validate_instance_type
    def save(self, instance: BaseModel) -> BaseModel:
        if isinstance(instance, Deployment):
            return self._create_deployment(instance)
        if isinstance(instance, Namespace):
            return self._create_namespace(instance)
        raise NotImplementedError

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
        if resource_type == Namespace:
            queryset = self._get_namespace(id=id)

        kwargs = self._validated_kwargs(resource_type, **kwargs)
        queryset = self._filter(queryset, **kwargs)
        if limit_ != -1:
            queryset = queryset[skip_ : skip_ + limit_]

        if first:
            return queryset[0] if queryset else None
        return queryset

    @validate_resource_type
    def delete(self, resource_type: Type, id: BaseModel) -> None:
        if resource_type == Deployment:
            return self._delete_deployment(id)
        if resource_type == Namespace:
            return self._delete_namespace(id)
        raise NotImplementedError

    def get_deployment_logs(
        self,
        id: str,
        limit: Optional[int] = None,
        since: Optional[str] = None,
        previous: bool = False,
    ) -> List[str]:
        return [f"[FAKE] log for {id}"]

    def get_capacity_options(self):
        return {
            "small": {
                "cpu_limit": 1.0,
                "memory_limit": "750Mi",
                "cpu_requested": 0.5,
                "memory_requested": "500Mi",
            },
            "medium": {
                "cpu_limit": 3.0,
                "memory_limit": "6000Mi",
                "cpu_requested": 2.0,
                "memory_requested": "4000Mi",
            },
        }

    @classmethod
    def verify_header(cls, payload: bytes, signature: str) -> None:
        pass

    def create_rule_checker(self, instance):
        logger.info("[FAKE] Rule Checker created")

    def delete_rule_checker(self):
        logger.info("[FAKE] Rule Checker deleted")

    def get_rule_checker(self):
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "labels": {
                    "access_id": "57e45010-ad7a-4dce-b759-98ec4f77a079",
                    "component_capacity": "",
                    "id": "orghhmefmw2iofgdjqw",
                    "log_level": "20",
                    "type": "RuleChecker",
                },
                "name": "rule-checker",
                "namespace": "orghhmefmw2iofgdjqw",
            },
            "spec": {}
        }
