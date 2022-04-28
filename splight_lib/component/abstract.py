import sys
import time
import pandas as pd
import builtins
from typing import Optional, Type, List
from tempfile import NamedTemporaryFile
from abc import ABCMeta
import json
from splight_lib.database import DatabaseClient
from splight_lib.datalake import DatalakeClient
from splight_lib.deployment import DeploymentClient
from splight_lib.storage import StorageClient
from splight_lib.communication import (
    InternalCommunicationClient,
    ExternalCommunicationClient,
)
from splight_lib.execution import Thread, ExecutionClient
from splight_lib import logging
from splight_lib.logging import logging
import splight_models as models
from splight_models import Message, VariableDataFrame, Variable, Deployment, Runner


logger = logging.getLogger()


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


class AbstractComponent(HealthCheckMixin, metaclass=ABCMeta):
    collection_name = 'default'
    managed_class: Type = None

    def __init__(self,
                 instance_id: str,
                 run_spec: str,
                 namespace: Optional[str] = 'default',
                 *args, **kwargs):

        # Params to start Lib clients
        # TODO https://splight.atlassian.net/browse/FAC-343
        self.namespace = namespace
        self.instance_id = instance_id

        # Lib clients
        self.database_client = DatabaseClient(namespace)
        self.storage_client = StorageClient(namespace)
        self.datalake_client = DatalakeClient(namespace)
        self.deployment_client = DeploymentClient(namespace=namespace)
        self.internal_comm_client = InternalCommunicationClient(namespace)
        self.external_comm_client = ExternalCommunicationClient(namespace)
        self.execution_client = ExecutionClient(namespace)

        # Main execution
        self.execution_client.start(Thread(target=self.listen_commands))
        self.execution_client.start(Thread(target=self.listen_internal_commands))

        super().__init__(*args, **kwargs)
        self._spec = Deployment(**json.loads(run_spec))
        self._load_metadata()
        self._load_parameters()
        self._load_context()
        self.collection_name = str(self.managed_class) + self.instance_id

    def _load_metadata(self):
        self._version = self._spec.version
        self.managed_class = getattr(models, self._spec.type, Runner)

    def _load_context(self):
        self.namespace = self._spec.namespace
        self.instance_id = self._spec.external_id

    def _load_parameters(self):
        _parameters = self._spec.parameters
        for p in _parameters:
            name = p.name
            value = getattr(builtins, p.type, str)(p.value)
            setattr(self, name, value)

    @property
    def instance(self):
        return self.database_client.get(
            resource_type=self.managed_class,
            id=self.instance_id,
            first=True
        )

    def listen_commands(self) -> None:
        while True:
            data = self.external_comm_client.receive()
            logger.debug(f"Message received from queue {data}")
            msg = Message(**data)
            action, variables = msg.action, msg.variables
            handler = getattr(self, f'handle_{action}', None)
            if handler is None:
                logger.error(f"Handler not defined in class for action {action}. "
                             f"Please provide a function with name handle_{action}")
                continue
            handler(variables)

    def listen_internal_commands(self) -> None:
        while True:
            data = self.internal_comm_client.receive()
            logger.debug(f"Message received from internal queue {data}")
            msg = Message(**data)
            action, variables = msg.action, msg.variables
            handler = getattr(self, f'_handle_{action}', None)
            if handler is None:
                logger.error(f"Handler not defined in class for action {action}. "
                             f"Please provide a function with name _handle_{action}")
                continue
            handler(variables)

    def get_history(self, asset_id: str, attribute_ids: List[str], **kwargs) -> VariableDataFrame:
        return self.datalake_client.get_dataframe(
            resource_type=Variable,
            asset_id=asset_id,
            attribute_id__in=attribute_ids,
            **kwargs)

    def save_results(self, data: VariableDataFrame) -> None:
        self.datalake_client.save_dataframe(data, collection=self.collection_name)
