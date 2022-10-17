from splight_lib.component.abstract import AbstractComponent
from splight_models import SystemRunner


class AbstractSystemComponent(AbstractComponent):
    managed_class = SystemRunner

    def __init__(self, *args, **kwargs):
        super(AbstractSystemComponent, self).__init__(*args, **kwargs)

    def _load_instance_data(self):
        self.collection_name = "system"
        self.instance_id_ = None
