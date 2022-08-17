
from splight_lib.component.abstract import AbstractComponent
from splight_models import Algorithm


class AbstractAlgorithmComponent(AbstractComponent):
    managed_class = Algorithm

    def __init__(self, *args, **kwargs):
        super(AbstractAlgorithmComponent, self).__init__(*args, **kwargs)

        self.collection_name = str(self.instance_id)
        # TODO: move this to create index on organization creation
        self.datalake_client.create_index(self.collection_name, [('attribute_id', 1), ('asset_id', 1), ('timestamp', -1)])
