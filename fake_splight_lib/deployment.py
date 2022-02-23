from pydantic import BaseModel
from typing import List, Type
from splight_deployment.abstract import AbstractDeploymentClient
from splight_models import Deployment, Namespace
from splight_lib import logging


logger = logging.getLogger()


class FakeDeploymentClient(AbstractDeploymentClient):
    namespace = "default"
    deployments = {}
    namespaces = {}

    def _create_deployment(self, instance: Deployment) -> Deployment:
        logger.info("[FAKED] Applying fake deployment")
        self.deployments[instance.id] = instance.dict()
        return instance

    def _get_deployment(self, id: str = '') -> List[Deployment]:
        logger.info("[FAKED] Retrieving fake deployment")
        if id:
            return [value for key, value in self.deployments.items() if key == id]
        else:
            return [value for _, value in self.deployments.items()]

    def _delete_deployment(self, id: str) -> None:
        logger.info("[FAKED] Deleting fake deployment")
        try:
            del self.deployments[id]
        except KeyError:
            logger.warning(f"[FAKED] Deployment not present {id}")

    def _create_namespace(self, instance: Namespace) -> Namespace:
        self.namespaces[instance.id] = instance
        return instance

    def _get_namespace(self, id: str = '') -> List[Namespace]:
        logger.info("[FAKED] Retrieving fake deployment")
        if id:
            return [value for key, value in self.deployments.items() if key == id]
        else:
            return [value for _, value in self.deployments.items()]

    def _delete_namespace(self, id: str) -> None:
        logger.info("[FAKED] Deleting fake deployment")
        try:
            del self.namespaces[id]
        except KeyError:
            logger.warning(f"[FAKED] Deployment not present {id}")

    def save(self, instance: BaseModel) -> BaseModel:
        if isinstance(instance, Deployment):
            return self._create_deployment(instance)
        if isinstance(instance, Namespace):
            return self._create_namespace(instance)
        raise NotImplementedError

    def get(self, resource_type: Type, first: bool = False, id: str = '') -> List[BaseModel]:
        if resource_type == Deployment:
            return self._get_deployment(id=id)
        if resource_type == Namespace:
            return self._get_namespace(id=id)
        raise NotImplementedError

    def delete(self, resource_type: Type, instance: BaseModel) -> None:
        if resource_type == Deployment:
            return self._delete_deployment(instance)
        if resource_type == Namespace:
            return self._delete_namespace(instance)
        raise NotImplementedError
