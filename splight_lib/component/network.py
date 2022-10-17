from splight_models import Network
from splight_lib import logging
from splight_lib.component.abstract import AbstractComponent


logger = logging.getLogger()


class AbstractNetworkComponent(AbstractComponent):
    managed_class = Network

    def __init__(self, *args, **kwargs):
        super(AbstractNetworkComponent, self).__init__(*args, **kwargs)
        self.collection_name = str(self.instance_id)

    def _load_instance_data(self):
        self.collection_name = str(self.instance_id)
        self.communication_client_kwargs['instance_id'] = self.instance_id
