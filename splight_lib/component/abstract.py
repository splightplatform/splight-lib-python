import sys
import time
import pandas as pd
from abc import abstractmethod
from tempfile import NamedTemporaryFile
from typing import Optional, Type, List, Dict
from splight_lib.execution import ExecutionClient, Thread
from splight_lib.logging import logging
from splight_lib.settings import setup as default_setup
from splight_lib.shortcut import save_file as _save_file
from splight_models.notification import Notification
from splight_models import (
    Deployment,
    Notification,
    Parameter,
    StorageFile,
    RunnerDatalakeModel,
    Algorithm
)
from splight_models.runner import DATABASE_TYPES, STORAGE_TYPES, SIMPLE_TYPES
from collections import defaultdict
from pydantic import BaseModel
from functools import cached_property, partial


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
        self.execution_client.start(Thread(self.healthcheck, daemon=True))

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
    def _load_client_hooks(self):
        self.datalake_client.add_pre_hook("save", self.hook_insert_origin_save)
        self.datalake_client.add_pre_hook("save", self.hook_lock_save_collection)
        self.datalake_client.add_pre_hook("save_dataframe", self.hook_insert_origin_save_dataframe)
        self.datalake_client.add_pre_hook("save_dataframe", self.hook_lock_save_collection)

    def hook_insert_origin_save(self, *args, **kwargs):
        instances = kwargs.get("instances", [])
        for instance in instances:
            if not isinstance(instance, RunnerDatalakeModel):
                continue
            instance.instance_id = self.instance_id
            instance.instance_type = self.managed_class.__name__

        return args, kwargs

    def hook_insert_origin_save_dataframe(self, *args, **kwargs):
        dataframe = kwargs.get("dataframe")
        dataframe["instance_id"] = self.instance_id
        dataframe["instance_type"] = self.managed_class.__name__
        kwargs["dataframe"] = dataframe
        return args, kwargs

    def hook_lock_save_collection(self, *args, **kwargs):
        kwargs["collection"] = self.collection_name
        return args, kwargs


class UtilsMixin:
    def get_history(self, **kwargs) -> pd.DataFrame:
        return self.datalake_client.get_dataframe(collection="default", **kwargs)

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

        dataframe["output_format"] = output_model.__name__

        self.datalake_client.save_dataframe(
            dataframe=dataframe,
            collection=self.collection_name
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
        self._spec: Deployment = Deployment(**run_spec)
        self._setup = default_setup
        if initial_setup:
            self._setup.configure(initial_setup)

        self.version: str = self._spec.version
        self.namespace = self._spec.namespace
        self.instance_id = self._spec.external_id

        self._load_clients()
        self._load_client_hooks()
        self._load_spec_models()
        self._load_spec_bindings()
        super().__init__(*args, **kwargs)

    @property
    def spec(self) -> Deployment:
        return self._spec

    @property
    def setup(self):
        return self._setup
  
    @cached_property
    def instance(self):
        return self.database_client.get(
            resource_type=self.managed_class, id=self.instance_id, first=True
        )

    def _load_spec_models(self):
        raw_spec = self.spec.dict()
        self._retrieve_objects_in_input(raw_spec["input"])
        parsed_input = self._parse_input(raw_spec["input"])
        self.input = self._spec.input_model(**parsed_input)
        self.output = self._spec.output_model
        self.custom_types = self._spec.custom_types_model
        self.commands = self._spec.commands_model

    def _load_spec_bindings(self):
        for command in self.spec.commands:
            event_name = command.name.lower()
            _event_handler = getattr(self, event_name, None)
            if _event_handler is None:
                logger.warning(f"Event handler for {event_name} not present skipping binding. Please add a handler for this type of event.")
                continue
            event_model = getattr(self.commands, command.name.title())
            event_handler = partial(self.communication_client.default_handler, _event_handler, event_model)
            self.communication_client.bind(event_name, event_handler)

    def _load_clients(self):
        self.database_client = self.setup.DATABASE_CLIENT(namespace=self.namespace)
        self.datalake_client = self.setup.DATALAKE_CLIENT(namespace=self.namespace)
        self.deployment_client = self.setup.DEPLOYMENT_CLIENT(namespace=self.namespace)
        self.storage_client = self.setup.STORAGE_CLIENT(namespace=self.namespace)
        self.communication_client = self.setup.COMMUNICATION_CLIENT(namespace=self.namespace)
        self.communication_client.reference_id = self.instance_id
        self.execution_client = ExecutionClient(namespace=self.namespace)

    def _retrieve_objects_in_input(self, parameters: List):
        ids = {
            "database": defaultdict(list),
            "storage": defaultdict(list),
        }
        self._get_ids(parameters, ids)
        objects = self._retrieve_objects(ids)
        objects[None] = None
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
            multiple = parameter["multiple"]

            if (value is [] or value == '') and type != "str":
                value = None

            if type in SIMPLE_TYPES:
                parameters_dict[name] = value
            elif multiple:
                parameters_dict[name] = [self._parse_input(val) for val in value]
            else:
                parameters_dict[name] = self._parse_input(value)

        return parameters_dict
