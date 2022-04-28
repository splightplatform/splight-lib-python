from splight_models import Network
from splight_lib import logging
from .abstract import AbstractComponent


logger = logging.getLogger()


class AbstractNetworkComponent(AbstractComponent):
    managed_class = Network
    rules = []

    # def __init__(self, *args, **kwargs):
    #     super(AbstractNetworkComponent, self).__init__(*args, **kwargs)
    #     self.execution_client.start(Thread(target=self.refresh_rules_forever, daemon=True))

    # def refresh_rules_forever(self) -> None:
    #     time_interval = 10
    #     while True:
    #         related_servers = self.database_client.get(Connector, network_id=self.instance_id)
    #         logger.debug(f"Related servers found {len(related_servers)}")
    #         for srv in related_servers:
    #             deployment = self.deployment_client.get(
    #                 Deployment,
    #                 type="Connector",
    #                 external_id=srv.id,
    #                 first=True
    #             )
    #             srv.host = self.deployment_client._get_service_name(deployment) if deployment else None
    #         self.rules = [srv for srv in related_servers if srv.host]
    #         logger.debug(self.rules)
    #         time.sleep(time_interval)
