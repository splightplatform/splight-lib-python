from django.db.models import Model
from typing import Dict
from splight_deployment.abstract import AbstractDeploymentClient
from splight_deployment.status import Status
from splight_lib import logging


logger = logging.getLogger()


class FakeDeploymentClient(AbstractDeploymentClient):
    namespace = "default"
    deployments = {}

    def get_deployment_name(self, instance: Model) -> str:
        return f"deployment-{instance.id}"

    def get_service_name(self, instance: Model) -> str:
        return f"service-{instance.id}"

    def get_deployment_yaml(self, instance: Model) -> str:
        return ""

    def apply_deployment(self, instance: Model) -> None:
        logger.info("Applying fake deployment")
        self.deployments[instance.id] = "running"

    def delete_deployment(self, instance: Model) -> None:
        logger.info("Deleting fake deployment")
        try:
            del self.deployments[instance.id]
        except KeyError:
            logger.info(f"Deployment not present {instance.id}")
            

    def get_info(self, instance: Model, kind: str) -> Dict:
        pass

    def get_status(self, instance: Model) -> Status:
        deployment = self.deployments.get(instance, None)
        status = deployment if deployment is not None else "Stopped"
        deployment_name = self.get_deployment_name(instance)
        return Status(deployment_name=deployment_name, status=status)

    def get_logs(self, instance: Model) -> str:
        return "Nothing to log"
