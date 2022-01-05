import tempfile
import os
import logging
import json
import subprocess as sp
from jinja2 import Template
from pprint import pprint as print
from .status import Status
from .abstract import AbstractDeploymentClient


class KubernetesClient(AbstractDeploymentClient):
    logger = logging.getLogger(__name__)
    namespace = "default"

    def get_deployment_name(self, instance):
        classname = instance.__class__.__name__.lower()
        id = str(instance.id).lower()
        return f"deployment-{classname}-{id}"

    def get_service_name(self, instance):
        classname = instance.__class__.__name__.lower()
        id = str(instance.id).lower()
        return f"service-{classname}-{id}"

    def get_deployment_yaml(self, instance):
        template_path = f"deployment/templates/{instance.__class__.__name__}.yaml"
        with open(template_path, "r+") as f:
            source = f.read()
        template = Template(source)
        return template.render(
            instance=instance,
            namespace_name=self.namespace,
            deployment_name=self.get_deployment_name(instance),
            service_name=self.get_service_name(instance),
        )

    def apply_deployment(self, instance):
        yaml_payload = self.get_deployment_yaml(instance)
        with tempfile.NamedTemporaryFile("w+") as fp:
            fp.write(yaml_payload)
            fp.seek(0)
            result = os.system(f"kubectl apply -f {fp.name}")
            self.logger.info(result)

    def delete_deployment(self, instance):
        deployment = self.get_deployment_name(instance)
        result = os.system(f"kubectl delete deployment {deployment} -n {self.namespace}")
        result = os.system(f"kubectl delete service {deployment} -n {self.namespace}")
        self.logger.info(result)

    def get_info(self, instance, kind):
        deployment_name = self.get_deployment_name(instance)
        result = sp.getoutput(f"kubectl get {kind} -n {self.namespace} --selector app={deployment_name} -o json")
        return json.loads(result)

    def get_status(self, instance) -> Status:
        result = self.get_info(instance, "pods")
        status_data = result["items"][0]["status"]["containerStatuses"][0]["state"]

        id = instance.pk
        deployment_name = self.get_deployment_name(instance)
        status_type = list(status_data.keys())[0]
        detail = status_data[status_type].get("reason", "")
        status: Status = Status(id=id, deployment_name=deployment_name, status=status_type, detail=detail)
        return status

    def get_logs(self, instance):
        deployment_name = self.get_deployment_name(instance)
        result = sp.getoutput(
            f"kubectl logs -n {self.namespace} --selector app={deployment_name} --all-containers=true"
        )
        return result
