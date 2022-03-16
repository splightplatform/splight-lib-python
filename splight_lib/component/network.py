import time
from typing import Optional
from splight_lib.execution import Thread
from splight_models.network import Network
from splight_models import (
    ServerConnector,
    Deployment
)
from .abstract import AbstractComponent


class AbstractNetworkComponent(AbstractComponent):
    managed_class = Network
    rules = []

    def __init__(self,
                 instance_id: str,
                 namespace: Optional[str] = 'default'):
        super(AbstractNetworkComponent, self).__init__(instance_id, namespace)
        self.execution_client.start(Thread(target=self.refresh_rules_forever))

    def refresh_rules_forever(self) -> None:
        while True:
            # Get related servers available in this Network
            related_servers = self.database_client.get(ServerConnector, network_id=self.instance_id)
            for srv in related_servers:
                deployment = self.deployment_client.get(
                    Deployment,
                    type="ServerConnector",
                    external_id=srv.id,
                    first=True
                )
                srv.host = self.deployment_client._get_service_name(deployment) if deployment else None
            self.rules = [srv for srv in related_servers if srv.host]
            time.sleep(10)
