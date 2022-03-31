import builtins
from .abstract import AbstractComponent
from splight_models import Runner


class AbstractAlgorithmComponent(AbstractComponent):
    managed_class = Runner

    def __init__(self, run_spec, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._spec = run_spec
        self._load_metadata()
        self._load_parameters()
        self._load_context()
        self.collection_name = self._name + self.instance_id

    def _load_metadata(self):
        self._name = self._spec.name
        self._version = self._spec.version
        self.managed_class = self._spec.type

    def _load_context(self):
        self.namespace = self._spec.namespace

    def _load_parameters(self):
        _parameters = self._spec.parameters
        for p in _parameters:
            name = p.name
            value = getattr(builtins, p.type, "str")(p.value)
            setattr(self, name, value)
