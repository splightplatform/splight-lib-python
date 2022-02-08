from typing import List, Dict
from splight_deployment.abstract import AbstractDeploymentClient
from splight_deployment.models import Deployment, Namespace
from splight_lib import logging


logger = logging.getLogger()


class FakeDeploymentClient(AbstractDeploymentClient):
    namespace = "default"
    deployments = {}
    namespaces = {}

    @classmethod
    def create_namespace(cls, namespace: str, environment: Dict = {}) -> "FakeDeploymentClient":
        logger.info("[FAKED] Configure fake namespace")
        client = cls()
        client.namespace = namespace
        return client

    def create(self, instance: Deployment) -> None:
        logger.info("[FAKED] Applying fake deployment")
        self.deployments[instance.id] = instance.dict()

    def get(self, id: str = '') -> List[Deployment]:
        logger.info("[FAKED] Retrieving fake deployment")
        if id:
            return [value for key, value in self.deployments.items() if key == id]
        else:
            return [value for _, value in self.deployments.items()]

    def delete(self, id: str) -> None:
        logger.info("[FAKED] Deleting fake deployment")
        try:
            del self.deployments[id]
        except KeyError:
            logger.warning(f"[FAKED] Deployment not present {id}")

    def create_namespace(self, namespace: Namespace):
        self.namespaces[namespace] = namespace

    def get_namespace(self, id: str = '') -> List[Namespace]:
        logger.info("[FAKED] Retrieving fake deployment")
        if id:
            return [value for key, value in self.deployments.items() if key == id]
        else:
            return [value for _, value in self.deployments.items()]

    def delete_namespace(self, id: str) -> None:
        logger.info("[FAKED] Deleting fake deployment")
        try:
            del self.namespaces[id]
        except KeyError:
            logger.warning(f"[FAKED] Deployment not present {id}")
