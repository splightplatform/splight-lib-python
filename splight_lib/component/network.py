from splight_models import Network
from splight_lib import logging
from splight_lib.component.abstract import AbstractComponent


logger = logging.getLogger()


class AbstractNetworkComponent(AbstractComponent):
    managed_class = Network

    def __init__(self, *args, **kwargs):
        super(AbstractNetworkComponent, self).__init__(*args, **kwargs)
        self.collection_name = str(self.instance_id)
        # TODO: move this to create index on organization creation
        # TODO: create index based on output
        # self.datalake_client.create_index('network', [('timestamp', -1)])
