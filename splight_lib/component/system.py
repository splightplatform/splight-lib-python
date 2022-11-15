from splight_lib.component.abstract import AbstractComponent
from splight_models.component import System


class AbstractSystemComponent(AbstractComponent):
    managed_class = System

    def __init__(self, *args, **kwargs):
        super(AbstractSystemComponent, self).__init__(*args, **kwargs)

    def _load_instance_data(self):
        self.collection_name = "system"
        self.communication_client_kwargs['instance_id'] = None
