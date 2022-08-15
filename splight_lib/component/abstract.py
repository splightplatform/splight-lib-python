import sys
import time
import json
from abc import ABCMeta, abstractmethod
from typing import Optional, Type, List, Dict
from tempfile import NamedTemporaryFile
from functools import wraps
from splight_models import (
    VariableDataFrame,
    Variable,
    Deployment,
    StorageFile,
)
from splight_lib.shortcut import (
    save_file as _save_file,
    notify as _notify
)
from splight_lib.settings import setup
from splight_lib.execution import Thread, ExecutionClient
from splight_lib.logging import logging
from splight_models.notification import Notification


logger = logging.getLogger()


def wait_until_initialized(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        while not self._initialized:
            time.sleep(0.1)
        return func(self, *args, **kwargs)
    return wrapper


class InitializedMixinMeta(ABCMeta):
    def __call__(self, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)
        obj._initialized = True
        return obj


class InitializedMixin(metaclass=InitializedMixinMeta):
    _initialized = False
    __slots__ = ()


class HealthCheckMixin:
    healthcheck_interval = 5

    def __init__(self):
        self.health_file = NamedTemporaryFile(prefix="healthy_")
        self.execution_client.start(Thread(self.healthcheck))

    def healthcheck(self) -> None:
        while True:
            if not self.execution_client.healthcheck():
                logger.error("A task has failed")
                self.health_file.close()
                logger.error(f"Healthcheck file removed: {self.health_file}")
                sys.exit()
            time.sleep(self.healthcheck_interval)


class AbstractComponent(HealthCheckMixin, InitializedMixin):
    collection_name = 'default'
    managed_class: Type = None

    def __init__(self,
                 instance_id: str,
                 run_spec: str,
                 namespace: Optional[str] = 'default',
                 *args, **kwargs):

        self.namespace = namespace
        self.instance_id = instance_id
        self.collection_name = str(self.instance_id)
        self._setup = setup
        self._load_clients()
        self._load_hooks()

        super().__init__(*args, **kwargs)

        self._spec = Deployment(**json.loads(run_spec))
        self._load_metadata()
        self._load_parameters()
        self._load_context()

    def hook_insert_origin(self, *args, **kwargs):
        """
        Hook to insert instance_id on save
        """
        instances = kwargs.get("instances", [])
        variables = [v for v in instances if isinstance(v, Variable)]
        for variable in variables:
            variable.instance_id = self.instance_id
            variable.instance_type = self.managed_class.__name__
        return args, kwargs

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

    def _load_hooks(self):
        self.datalake_client.add_pre_hook('save', self.hook_insert_origin)

    def _load_clients(self):
        self.database_client = self.setup.DATABASE_CLIENT(self.namespace)
        self.storage_client = self.setup.STORAGE_CLIENT(namespace=self.namespace)
        self.datalake_client = self.setup.DATALAKE_CLIENT(self.namespace)
        self.notification_client = self.setup.NOTIFICATION_CLIENT(namespace=self.namespace)
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
        return _notify(
            notification=notification,
            database_client=self.database_client,
            notification_client=self.notification_client,
            datalake_client=self.datalake_client,
        )

    @abstractmethod
    def start(self):
        pass