from typing import List
from splight_deployment.abstract import AbstractDeploymentClient
from splight_deployment.models import Deployment, DeploymentInfo
from splight_lib import logging


logger = logging.getLogger()


class FakeDeploymentClient(AbstractDeploymentClient):
    namespace = "default"
    deployments = {}

    def create(self, instance: Deployment) -> DeploymentInfo:
        logger.info("[FAKED] Applying fake deployment")
        return DeploymentInfo(
            name="name",
            namespace=self.namespace,
            service="service_name",
            template=None,
            **instance.dict(),
        )

    def apply(self, info: DeploymentInfo) -> None:
        logger.info("[FAKED] Applying fake deployment")
        self.deployments[info.id] = info

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

