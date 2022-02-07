import tempfile
import json
import os
import logging
from pathlib import Path
import subprocess as sp
from jinja2 import Template
from typing import List, Dict
from splight_deployment.models import Deployment, DeploymentInfo
from splight_deployment.abstract import AbstractDeploymentClient
from .exceptions import MissingTemplate


logger = logging.getLogger(__name__)


class KubernetesClient(AbstractDeploymentClient):
    directory = Path(__file__).resolve().parent
    TEMPLATES_FOLDER = "templates"

    def __init__(self,
                 namespace: str = "default",
                 config_map: str = "splight-config",
                 service_account: str = "splight-sa") -> None:
        super().__init__(namespace)
        self.namespace = namespace.lower().replace("_", "")
        self.config_map = config_map
        self.service_account = service_account

    @classmethod
    def configure(cls, namespace: str, environment: Dict = {}) -> "KubernetesClient":
        client = cls(namespace)
        cm_template = client._get_template('Namespace')
        client._apply_yaml(cm_template.render(
            namespace=namespace
        ))
        cm_template = client._get_template('ConfigMap')
        client._apply_yaml(cm_template.render(
            configmap=client.config_map,
            environment=environment
        ))
        sa_template = client._get_template('ServiceAccount')
        client._apply_yaml(sa_template.render(
            serviceaccount=client.service_account,
            role_arn=environment.get("SERVICE_ACCOUNT_ROLE_ARN")
        ))
        return client

    def _get_deployment_name(self, instance: Deployment):
        id = str(instance.id).lower()
        type_id = str(instance.type).lower()
        return f"deployment-{type_id}-{id}"

    def _get_service_name(self, instance: Deployment):
        id = str(instance.id).lower()
        type_id = str(instance.type).lower()
        return f"service-{type_id}-{id}"

    def _get_template(self, name) -> Template:
        template_path = os.path.join(self.directory, self.TEMPLATES_FOLDER, f"{name}.yaml")
        if not os.path.exists(template_path):
            raise MissingTemplate(f"Unable to find template {template_path}")
        with open(template_path, "r+") as f:
            content = f.read()
        return Template(content)

    def _apply_yaml(self, spec: str):
        with tempfile.NamedTemporaryFile("w+") as fp:
            fp.write(spec)
            fp.seek(0)
            result = os.system(f"kubectl apply -n {self.namespace} -f {fp.name}")
            logger.info(result)

    def create(self, instance: Deployment) -> DeploymentInfo:
        template = self._get_template(name = instance.type)

        return DeploymentInfo(
            name=self._get_deployment_name(instance),
            namespace=self.namespace,
            service=self._get_service_name(instance),
            template=template,
            **instance.dict()
        )

    def apply(self, info: DeploymentInfo) -> None:
        spec = info.template.render(
            configmap = self.config_map,
            serviceaccount = self.service_account,
            **info.dict()
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
        result = os.system(f"kubectl delete deployment --selector=id={id} -n {self.namespace}")
        result = os.system(f"kubectl delete service --selector=id={id} -n {self.namespace}")
        logger.info(result)