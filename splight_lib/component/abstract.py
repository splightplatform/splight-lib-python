from abc import abstractmethod
import sys
import time
import json
from typing import Optional, Type, List, Dict
from tempfile import NamedTemporaryFile
from splight_models import (
    VariableDataFrame,
    Variable,
    Deployment,
    StorageFile,
)
from splight_lib.shortcut import (
    save_file as _save_file
)
from splight_lib.settings import setup
from splight_lib.execution import Thread, ExecutionClient
from splight_lib.logging import logging
from splight_models.notification import Notification


logger = logging.getLogger()


class RunnableMixin:
    healthcheck_interval = 5

    def __init__(self):
        self.health_file = NamedTemporaryFile(prefix="healthy_")
        self.execution_client.start(Thread(self.healthcheck))

    def healthcheck(self) -> None:
        self.terminated = False
        while not self.terminated:
            if not self.execution_client.healthcheck():
                logger.error("A task has failed")
                self.health_file.close()
                logger.error(f"Healthcheck file removed: {self.health_file}")
                sys.exit()
            time.sleep(self.healthcheck_interval)

    @abstractmethod
    def start(self):
        pass

    def terminate(self):
        self.terminated = True


class HooksMixin:
    def _load_hooks(self):
        self.datalake_client.add_pre_hook('save', self.hook_insert_origin)

    def hook_insert_origin(self, *args, **kwargs):
        instances = kwargs.get("instances", [])
        variables = [v for v in instances if isinstance(v, Variable)]
        for variable in variables:
            variable.instance_id = self.instance_id
            variable.instance_type = self.managed_class.__name__
        return args, kwargs


class UtilsMixin:
    def get_history(self,
                    asset_id: Optional[str] = None,
                    attribute_ids: Optional[List[str]] = None,
                    algorithm_id: Optional[str] = None,
                    **kwargs) -> VariableDataFrame:
        if asset_id:
            kwargs["asset_id"] = asset_id
        if algorithm_id:
            kwargs["collection"] = algorithm_id
        if attribute_ids:
            kwargs["attribute_ids"] = attribute_ids
        return self.datalake_client.get_dataframe(resource_type=Variable, **kwargs)

    def save_results(self, data: VariableDataFrame) -> None:
        self.datalake_client.save_dataframe(data, collection=self.collection_name)

    def save_file(self,
                  filename: str,
                  prefix: Optional[str],
                  asset_id: Optional[str],
                  attribute_id: Optional[str],
                  path: str,
                  args: Dict) -> StorageFile:
        return _save_file(
            self.storage_client,
            self.datalake_client,
            filename,
            prefix,
            asset_id,
            attribute_id,
            path,
            args
        )

    def notify(self, notification: Notification):
        return self.database_client.save(notification)


class AbstractComponent(RunnableMixin, HooksMixin, UtilsMixin):
    collection_name = 'default'
    managed_class: Type = None

    def __init__(self,
                 instance_id: str,
                 run_spec: str,
                 namespace: Optional[str] = 'default',
                 *args, **kwargs):

        self.namespace = namespace
        self.instance_id = instance_id

        self._setup = setup
        self._load_clients()
        self._load_hooks()

        super().__init__(*args, **kwargs)

        self._spec = Deployment(**json.loads(run_spec))
        self._load_metadata()
        self._load_parameters()
        self._load_context()

    def _load_metadata(self):
        self._version = self._spec.version

    def _load_context(self):
        self.namespace = self._spec.namespace
        self.instance_id = self._spec.external_id

    def _load_parameters(self):
        _parameters = self._spec.parameters
        for p in _parameters:
            name = p.name
            value = p.value
            setattr(self, name, value)

    def _load_clients(self):
        self.database_client = self.setup.DATABASE_CLIENT(self.namespace)
        self.datalake_client = self.setup.DATALAKE_CLIENT(self.namespace)
        self.deployment_client = self.setup.DEPLOYMENT_CLIENT(self.namespace)
        self.storage_client = self.setup.STORAGE_CLIENT(namespace=self.namespace)
        self.execution_client = ExecutionClient(self.namespace)

    @property
    def setup(self):
        return self._setup

    @setup.setter
    def setup(self, new_setup):
        self._setup.configure(new_setup)
        self._load_clients()
        self._load_hooks()

    @property
    def instance(self):
        return self.database_client.get(
            resource_type=self.managed_class,
            id=self.instance_id,
            first=True
        )
