
from .abstract import AbstractComponent
from splight_models import Algorithm


class AbstractAlgorithmComponent(AbstractComponent):
    managed_class = Algorithm

    def __init__(self, *args, **kwargs):
        super(AbstractAlgorithmComponent, self).__init__(*args, **kwargs)
        self.datalake_client.create_index(self.collection_name, [('asset_id', 1), ('timestamp', -1)])