import tempfile
import json
import os
import logging
from pathlib import Path
import subprocess as sp
from jinja2 import Template
from typing import List
from splight_deployment.models import Deployment, DeploymentInfo
from splight_deployment.abstract import AbstractDeploymentClient
from .exceptions import MissingTemplate


logger = logging.getLogger(__name__)


class KubernetesClient(AbstractDeploymentClient):
    directory = Path(__file__).resolve().parent
    TEMPLATES_FOLDER = "templates"

    def __init__(self, namespace: str = "default") -> None:
        super().__init__(namespace)
        self.namespace = namespace.lower().replace("_", "")

    def _get_deployment_name(self, instance: Deployment):
        id = str(instance.id).lower()
        type_id = str(instance.type).lower()
        return f"deployment-{type_id}-{id}"

    def _get_service_name(self, instance: Deployment):
        id = str(instance.id).lower()
        type_id = str(instance.type).lower()
        return f"service-{type_id}-{id}"

    def setup(self):
        os.system(f"kubectl create namespace {self.namespace}")
        # TODO complete this
        # os.system(f"kubectl create secret")
        # os.system(f"kubectl create configmap")
        # os.system(f"kubectl create sa")

    def create(self, instance: Deployment) -> DeploymentInfo:
        template_path = os.path.join(self.directory, self.TEMPLATES_FOLDER, f"{instance.type}.yaml")
        if not os.path.exists(template_path):
            raise MissingTemplate(f"Unable to find template {template_path}")

        with open(template_path, "r+") as f:
            source = f.read()

        return DeploymentInfo(
            name=self._get_deployment_name(instance),
            namespace=self.namespace,
            service=self._get_service_name(instance),
            template=Template(source),
            **instance.dict()
        )

    def apply(self, info: DeploymentInfo) -> None:
        with tempfile.NamedTemporaryFile("w+") as fp:
            fp.write(info.spec)
            fp.seek(0)
            result = os.system(f"kubectl apply -f {fp.name}")
            logger.info(result)

    def get(self, id: str = '') -> List[Deployment]:
        cmd = f"kubectl get pod -n {self.namespace} -o json"
        if id:
            cmd += f" --selector=id={id}"
        result = sp.getoutput(cmd)
        data = json.loads(result)
        data = data['items'] if 'items' in data.keys() else [data]
        return [Deployment(**item['metadata']['labels']) for item in data]

    def delete(self, id: str) -> None:
        result = os.system(f"kubectl delete deployment --selector=id={id} -n {self.namespace}")
        result = os.system(f"kubectl delete service --selector=id={id} -n {self.namespace}")
        logger.info(result)