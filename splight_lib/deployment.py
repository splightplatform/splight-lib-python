
import ast

import os

from fake_splight_lib.deployment import FakeDeploymentClient
from splight_deployment import KubernetesClient, DeploymentInfo, Deployment

DeploymentClient = KubernetesClient

if ast.literal_eval(os.getenv("FAKE_DEPLOYMENT", "True")):
    DeploymentClient = FakeDeploymentClient

__all__ = [
    Deployment,
    DeploymentInfo,
    DeploymentClient
]