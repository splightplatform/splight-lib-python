
from splight_lib.component.abstract import AbstractComponent
from splight_models import Algorithm


class AbstractAlgorithmComponent(AbstractComponent):
    managed_class = Algorithm

    def __init__(self, *args, **kwargs):
        super(AbstractAlgorithmComponent, self).__init__(*args, **kwargs)

        self.collection_name = str(self.instance_id)

    def _load_instance_data(self):
        self.collection_name = str(self.instance_id)
        self.communication_client_kwargs['instance_id'] = self.instance_id
