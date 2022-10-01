from splight_lib.component.abstract import AbstractComponent
from splight_models import SystemRunner


class AbstractSystemComponent(AbstractComponent):
    managed_class = SystemRunner

    def __init__(self, *args, **kwargs):
        super(AbstractSystemComponent, self).__init__(*args, **kwargs)

        self.collection_name = "system"
        # TODO: move this to create index on organization creation
        # TODO: create index based on output
        # self.datalake_client.create_index(self.collection_name, [('attribute_id', 1), ('asset_id', 1), ('timestamp', -1)])
