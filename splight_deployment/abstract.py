from django.db.models import Model
from abc import ABC, abstractmethod
from typing import Dict
from .status import Status


class AbstractDeploymentClient(ABC):

    namespace = "default"

    @abstractmethod
    def get_deployment_name(self, instance: Model) -> str:
        pass

    @abstractmethod
    def get_service_name(self, instance: Model) -> str:
        pass

    @abstractmethod
    def get_deployment_yaml(self, instance: Model) -> Dict:
        pass

    @abstractmethod
    def apply_deployment(self, instance: Model) -> None:
        pass

    @abstractmethod
    def delete_deployment(self, instance: Model) -> None:
        pass

    @abstractmethod
    def get_info(self, instance: Model, kind: str) -> Dict:
        pass

    @abstractmethod
    def get_status(self, instance: Model) -> Status:
        pass

    def get_logs(self, instance: Model) -> str:
        pass
