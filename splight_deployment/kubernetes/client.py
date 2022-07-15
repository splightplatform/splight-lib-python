import tempfile
import json
import os
import logging
import subprocess as sp
import uuid
from pydantic import BaseModel
from pathlib import Path
from jinja2 import Template
from typing import List, Type, Optional

from pyparsing import Opt
from splight_models import Deployment, Namespace
from splight_deployment.abstract import AbstractDeploymentClient
from .exceptions import MissingTemplate
from client import validate_instance_type, validate_resource_type
from splight_models.query import QuerySet
logger = logging.getLogger(__name__)


class KubernetesClient(AbstractDeploymentClient):
    TEMPLATES_FOLDER = os.path.join(Path(__file__).resolve().parent, "templates")
    DOCKER_REGISTRY = os.getenv("DOCKER_REGISTRY", "609067598877.dkr.ecr.us-east-1.amazonaws.com")
    valid_classes = [Deployment, Namespace]

    def __init__(self,
                 config_map: str = "splight-config",
                 service_account: str = "splight-sa",
                 *args,
                 **kwargs) -> None:
        super(KubernetesClient, self).__init__(*args, **kwargs)
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

    def _get_docker_image(self, instance: Deployment):
        image = f"splight-runner:latest"
        if self.DOCKER_REGISTRY:
            return f"{self.DOCKER_REGISTRY}/{image}"
        return image

    def _get_run_spec(self, instance: Deployment):
        return instance.json()

    def _get_template(self, name) -> Template:
        template_path = os.path.join(self.TEMPLATES_FOLDER, f"{name}.yaml")
        if not os.path.exists(template_path):
            raise MissingTemplate(f"Unable to find template {template_path}")
        with open(template_path, "r+") as f:
            content = f.read()
        return Template(content)

    def _apply_yaml(self, spec: str, namespace: Optional[str] = None):
        namespace = namespace if namespace else self.namespace
        fp = tempfile.NamedTemporaryFile("w+", delete=False)
        fp.write(spec)
        name = fp.name
        fp.seek(0)
        fp.close()
        result = os.system(f"kubectl apply -f {name} -n {namespace}")
        logger.info(result)
        os.remove(name)

    def _create_deployment(self, instance: Deployment) -> Deployment:
        template = self._get_template(name=instance.type)
        instance.namespace = self.namespace
        spec = template.render(
            configmap=self.config_map,
            serviceaccount=self.service_account,
            service=self._get_service_name(instance),
            dockerimg=self._get_docker_image(instance),
            run_spec=self._get_run_spec(instance),
            **instance.dict()
        )
        self._apply_yaml(spec)
        return instance

    def _get_deployment(self, id: str = '') -> List[Deployment]:
        cmd = f"kubectl get deployment -n {self.namespace} -o json"
        if id:
            cmd += f" --selector=id={id}"
        result = sp.getoutput(cmd)
        data = json.loads(result)
        data = data['items'] if 'items' in data.keys() else [data]
        return [Deployment(**item['metadata']['labels']) for item in data]

    def _delete_deployment(self, id: str) -> None:
        os.system(f"kubectl delete deployment --selector=id={id} -n {self.namespace}")
        os.system(f"kubectl delete service --selector=id={id} -n {self.namespace}")

    def _create_namespace(self, instance: Namespace) -> Namespace:
        template = self._get_template(name='Namespace')
        spec = template.render(
            configmap=self.config_map,
            id=instance.id,
            serviceaccount=self.service_account,
            environment=instance.environment
        )
        self._apply_yaml(spec, namespace=instance.id)
        return instance

    def _get_namespace(self, id: str):
        cmd = f"kubectl get namespace -o json"
        if id:
            cmd += f" --selector=id={id}"
        result = sp.getoutput(cmd)
        data = json.loads(result)
        data = data['items'] if 'items' in data.keys() else [data]
        return [Namespace(**item['metadata']['labels'])
                for item in data
                if 'id' in item['metadata']['labels']]

    def _delete_namespace(self, id: str) -> None:
        os.system(f"kubectl delete namespace --selector=id={id}")

    @validate_instance_type
    def save(self, instance: BaseModel) -> BaseModel:
        if instance.id is None:
            instance.id = str(uuid.uuid4())
        if isinstance(instance, Deployment):
            return self._create_deployment(instance)
        if isinstance(instance, Namespace):
            return self._create_namespace(instance)

    def get(self, *args, **kwargs):
        return QuerySet(self, *args, **kwargs)

    @validate_resource_type
    def _get(self, resource_type: Type,
             id: str = '',
             first=False,
             limit: int = -1,
             skip_: int = 0,
             **kwargs) -> List[BaseModel]:
        if resource_type == Deployment:
            result: List[Deployment] = self._get_deployment(id=id)
        elif resource_type == Namespace:
            result: List[Namespace] = self._get_namespace(id=id)
        kwargs = self._validated_kwargs(resource_type, **kwargs)
        result = self._filter(result, **kwargs)
        if limit != -1:
            result = result[skip_:skip_ + limit]

        if first:
            return result[0] if result else None
        return result

    @validate_resource_type
    def delete(self, resource_type: Type, id: BaseModel) -> None:
        if resource_type == Deployment:
            return self._delete_deployment(id=id)
        if resource_type == Namespace:
            return self._delete_namespace(id=id)
        raise NotImplementedError

    def get_deployment_logs(self, id: str, limit: Optional[int] = None, since: Optional[str] = None) -> List[str]:
        cmd = f"kubectl logs --selector id={id} -n {self.namespace}"

        if limit:
            cmd += f" --tail {limit}"
        else:
            cmd += " --tail -1"

        if since:
            cmd += f" --since {since}"

        return sp.getoutput(cmd).split("\n")
