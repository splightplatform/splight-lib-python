import sys
import time
from abc import abstractmethod
import pandas as pd
from tempfile import NamedTemporaryFile
from typing import Optional, Type, List, Dict
from splight_lib.execution import ExecutionClient, Thread
from splight_lib.logging import logging
from splight_lib.settings import setup
from splight_lib.shortcut import save_file as _save_file
from splight_models.notification import Notification
from splight_models import (
    Deployment,
    Notification,
    Parameter,
    StorageFile,
    RunnerDatalakeModel,
    Variable,
    Algorithm
)
from splight_models.runner import DATABASE_TYPES, STORAGE_TYPES, SIMPLE_TYPES
from splight_lib.shortcut import (
    save_file as _save_file
)
from splight_lib.execution import Thread, ExecutionClient
from splight_lib.logging import logging
from collections import defaultdict
from pydantic import BaseModel
from functools import cached_property

logger = logging.getLogger()


class RunnableMixin:

    healthcheck_interval = 5
    _HEALTH_FILE_PREFIX = "healthy_"
    _STARTUP_FILE_PREFIX = "ready_"

    def __init__(self):
        self.health_file = NamedTemporaryFile(prefix=self._HEALTH_FILE_PREFIX)
        self.startup_file = NamedTemporaryFile(
            prefix=self._STARTUP_FILE_PREFIX
        )
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
        self.datalake_client.add_pre_hook("save", self.hook_insert_origin_save)
        self.datalake_client.add_pre_hook("save_dataframe", self.hook_insert_origin_save_dataframe)

    def hook_insert_origin_save(self, *args, **kwargs):
        instances = kwargs.get("instances", [])
        variables = [v for v in instances if isinstance(v, Variable)]
        for variable in variables:
            variable.instance_id = self.instance_id
            variable.instance_type = self.managed_class.__name__
        return args, kwargs

    def hook_insert_origin_save_dataframe(self, *args, **kwargs):
        dataframe = kwargs.get("dataframe")
        dataframe["instance_id"] = self.instance_id
        dataframe["instance_type"] = self.managed_class.__name__
        kwargs["dataframe"] = dataframe
        return args, kwargs


class UtilsMixin:
    def get_history(self, **kwargs) -> pd.DataFrame:
        return self.datalake_client.get_dataframe(collections="default", **kwargs)

    def get_results(self, algorithm: Algorithm, output_model: RunnerDatalakeModel, **kwargs) -> pd.DataFrame:
        if output_model != getattr(algorithm.output_model, output_model.__name__):
            raise ValueError(
                f"Output model {output_model.__name__} does not match algorithm output"
            )

        return self.datalake_client.get_dataframe(
            collection=algorithm.collection,
            output_format=output_model.__name__,
            **kwargs
        )

    def save_results(self, output_model: RunnerDatalakeModel, dataframe: pd.DataFrame) -> None:
        if output_model != getattr(self.output, output_model.__name__):
            raise ValueError(
                f"Output model {output_model.__name__} is not defined in the output"
            )

        try:
            for _, row in dataframe.iterrows():
                output_model.parse_obj(row.to_dict())
        except Exception:
            raise ValueError(f"Invalid dataframe: does not match output format")

        self.datalake_client.save_dataframe(
            dataframe=dataframe, collection=self.collection_name
        )

    def save_file(
        self,
        filename: str,
        prefix: Optional[str],
        asset_id: Optional[str],
        attribute_id: Optional[str],
        path: str,
        args: Dict,
    ) -> StorageFile:
        return _save_file(
            self.storage_client,
            self.datalake_client,
            filename,
            prefix,
            asset_id,
            attribute_id,
            path,
            args,
        )

    def notify(self, notification: Notification):
        return self.database_client.save(notification)


class AbstractComponent(RunnableMixin, HooksMixin, UtilsMixin):
    collection_name = "default"
    managed_class: Type = None

    def __init__(self, run_spec: dict, initial_setup: Optional[dict] = None, *args, **kwargs):
        self._raw_spec = run_spec
        self._spec: Deployment = Deployment(**run_spec)

        self.namespace = self._spec.namespace
        self.instance_id = self._spec.external_id

        self._init_setup(initial_setup)
        self._load_metadata()
        self._load_models()

        super().__init__(*args, **kwargs)

    def _init_setup(self, initial_setup: Optional[dict] = None):
        self._setup = setup
        if initial_setup:
            self.setup = initial_setup

    def _load_metadata(self):
        self._version: str = self._spec.version

    def _load_models(self):
        self._retrive_objects_in_input(self._raw_spec["input"])
        parsed_input = self._parse_input(self._raw_spec["input"])
        self.input = self._spec.input_model(**parsed_input)
        self.output = self._spec.output_model
        self.custom_types = self._spec.custom_types_model

    def _load_clients(self):
        self.database_client = self.setup.DATABASE_CLIENT(namespace=self.namespace)
        self.datalake_client = self.setup.DATALAKE_CLIENT(namespace=self.namespace)
        self.deployment_client = self.setup.DEPLOYMENT_CLIENT(namespace=self.namespace)
        self.storage_client = self.setup.STORAGE_CLIENT(namespace=self.namespace)
        self.execution_client = ExecutionClient(namespace=self.namespace)

    @property
    def setup(self):
        return self._setup

    @ setup.setter
    def setup(self, new_setup):
        self._setup.configure(new_setup)
        self._load_clients()
        self._load_hooks()

    @ cached_property
    def instance(self):
        return self.database_client.get(
            resource_type=self.managed_class, id=self.instance_id, first=True
        )

    def _retrive_objects_in_input(self, parameters: List):
        ids = {
            "database": defaultdict(list),
            "storage": defaultdict(list),
        }
        self._get_ids(parameters, ids)
        objects = self._retrieve_objects(ids)
        self._complete_input_with_objects(parameters, objects)
        return parameters

    def _get_ids(self, parameters: List[Parameter], ids: Dict) -> None:
        for parameter in parameters:
            values = parameter["value"] if parameter["multiple"] else [parameter["value"]]

            if parameter["type"] in DATABASE_TYPES:
                for value in values:
                    ids["database"][parameter["type"]].append(value)
            elif parameter["type"] in STORAGE_TYPES:
                for value in values:
                    ids["storage"][parameter["type"]].append(value)
            elif parameter["type"] not in SIMPLE_TYPES:
                for value in values:
                    self._get_ids(value, ids)

    def _retrieve_objects(self, ids: Dict) -> Dict[str, BaseModel]:
        res: Dict = {}
        for type, ids_ in ids["database"].items():
            objs = self.database_client.get(DATABASE_TYPES[type], id__in=ids_)
            res.update({obj.id: obj for obj in objs})

        for type, ids_ in ids["storage"].items():
            objs = self.storage_client.get(STORAGE_TYPES[type], id__in=ids_)
            res.update({obj.id: obj for obj in objs})

        return res

    def _complete_input_with_objects(self, parameters: List[Parameter], objects: Dict) -> None:
        for parameter in parameters:
            if parameter["type"] in DATABASE_TYPES or parameter["type"] in STORAGE_TYPES:
                if parameter["multiple"]:
                    parameter["value"] = [objects[val] for val in parameter["value"]]
                else:
                    parameter["value"] = objects[parameter["value"]]

            elif parameter["type"] not in SIMPLE_TYPES:
                values = parameter["value"] if parameter["multiple"] else [parameter["value"]]
                for value in values:
                    self._complete_input_with_objects(value, objects)

    def _parse_input(self, parameters: List) -> Dict:
        parameters_dict: Dict = {}

        for parameter in parameters:
            type = parameter["type"]
            name = parameter["name"]
            value = parameter["value"]
            required = parameter["required"]
            multiple = parameter["multiple"]

            if not required and not value:
                parameters_dict[name] = None
            elif type in SIMPLE_TYPES:
                parameters_dict[name] = value
            elif multiple:
                parameters_dict[name] = [self._parse_input(val) for val in value]
            else:
                parameters_dict[name] = self._parse_input(value)

        return parameters_dict
