import tempfile
import json
import os
import logging
from pathlib import Path
import subprocess as sp
from jinja2 import Template
from typing import List
from splight_deployment.models import Deployment, Namespace
from splight_deployment.abstract import AbstractDeploymentClient
from .exceptions import MissingTemplate


logger = logging.getLogger(__name__)


class KubernetesClient(AbstractDeploymentClient):
    TEMPLATES_FOLDER = os.path.join(Path(__file__).resolve().parent, "templates")

    def __init__(self,
                 namespace: str = "default",
                 config_map: str = "splight-config",
                 service_account: str = "splight-sa") -> None:
        super().__init__(namespace)
        self.namespace = namespace.lower().replace("_", "")
        self.config_map = config_map
        self.service_account = service_account

    def _get_deployment_name(self, instance: Deployment):
        id = str(instance.id).lower()
        type_id = str(instance.type).lower()
        return f"deployment-{type_id}-{id}"

    def _get_service_name(self, instance: Deployment):
        id = str(instance.id).lower()
        type_id = str(instance.type).lower()
        return f"service-{type_id}-{id}"

    def _get_template(self, name) -> Template:
        template_path = os.path.join(self.TEMPLATES_FOLDER, f"{name}.yaml")
        if not os.path.exists(template_path):
            raise MissingTemplate(f"Unable to find template {template_path}")
        with open(template_path, "r+") as f:
            content = f.read()
        return Template(content)

    def _apply_yaml(self, spec: str):
        with tempfile.NamedTemporaryFile("w+") as fp:
            fp.write(spec)
            fp.seek(0)
            result = os.system(f"kubectl apply -f {fp.name} -n {self.namespace}")
            logger.info(result)

    def create(self, instance: Deployment) -> None:
        template = self._get_template(name=instance.type)
        spec = template.render(
            configmap = self.config_map,
            name=self._get_deployment_name(instance),
            namespace=self.namespace,
            service=self._get_service_name(instance),
            serviceaccount = self.service_account,
            **instance.dict()
        )
        self._apply_yaml(spec)

    def get(self, id: str = '') -> List[Deployment]:
        cmd = f"kubectl get pod -n {self.namespace} -o json"
        if id:
            cmd += f" --selector=id={id}"
        result = sp.getoutput(cmd)
        data = json.loads(result)
        data = data['items'] if 'items' in data.keys() else [data]
        return [Deployment(**item['metadata']['labels']) for item in data]

    def delete(self, id: str) -> None:
        os.system(f"kubectl delete deployment --selector=id={id} -n {self.namespace}")
        os.system(f"kubectl delete service --selector=id={id} -n {self.namespace}")

    def create_namespace(self, instance: Namespace):
        template = self._get_template(name='Namespace')
        spec = template.render(
            configmap = self.config_map,
            id=instance.id,
            serviceaccount = self.service_account,
            environment=instance.environment
        )
        self._apply_yaml(spec)

    def get_namespace(self, id: str = ''):
        cmd = f"kubectl get namespace -o json"
        if id:
            cmd += f" --selector=id={id}"
        result = sp.getoutput(cmd)
        data = json.loads(result)
        data = data['items'] if 'items' in data.keys() else [data]
        return [Namespace(**item['metadata']['labels']) for item in data]

    def delete_namespace(self, id: str) -> None:
        os.system(f"kubectl delete namespace --selector=id={id}")
