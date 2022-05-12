import os
from fake_splight_lib.deployment import FakeDeploymentClient
from splight_deployment import KubernetesClient, Namespace, Deployment

SELECTOR = {
    'fake': FakeDeploymentClient,
    'kubernetes': KubernetesClient,
}

DeploymentClient = SELECTOR.get(os.environ.get('DEPLOYMENT', 'fake'))


__all__ = [
    Deployment,
    Namespace,
    DeploymentClient
]
