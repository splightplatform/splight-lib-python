import sys
import time
import pandas as pd
from abc import abstractmethod
from tempfile import NamedTemporaryFile
from typing import Optional, Type, List, Dict, Tuple, Set, Any
from mergedeep import merge, Strategy as mergeStrategy
from collections import defaultdict
from pydantic import BaseModel
from functools import cached_property
from splight_lib.execution import ExecutionClient, Thread
from splight_lib.logging import logging
from splight_lib.settings import setup as default_setup
from splight_lib.shortcut import save_file as _save_file  # TODO unify storage with database
from splight_models import (
    Deployment,
    Notification,
    StorageFile,
    ComponentDatalakeModel,
    Algorithm,
    Command,
    ComponentObject,
)
from splight_models.communication import Operation
from splight_models.communication.events import EventNames, OperationTriggerEvent, OperationUpdateEvent
from splight_models.communication.models import OperationStatus
from splight_models.component import DATABASE_TYPES, NATIVE_TYPES, STORAGE_TYPES


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


class IndexMixin:
    def _load_client_indexes(self) -> None:
        indexes: List[Tuple[str, int]] = self.__get_indexes()
        logger.debug(f"Adding indexes: {indexes}")
        self.datalake_client.create_index(
            self.collection_name,
            indexes
        )

    def __get_indexes(self) -> List[Tuple[str, int]]:
        # order in indexes matters
        indexes: List[Tuple[str, int]] = [
            ("output_format", 1),
        ]
        unique_indexes: Set[str] = set()

        for output in self._spec.output:
            for field in output.fields:
                if field.filterable:
                    unique_indexes.add(field.name)

        for index in unique_indexes:
            indexes.append((index, 1))

        indexes.append(("timestamp", -1))

        return indexes


class HooksMixin:
    def _load_client_hooks(self):
        self.datalake_client.add_pre_hook("save", self.__hook_insert_origin_save)
        self.datalake_client.add_pre_hook("save", self.__hook_lock_save_collection)
        self.datalake_client.add_pre_hook("save_dataframe", self.__hook_insert_origin_save_dataframe)
        self.datalake_client.add_pre_hook("save_dataframe", self.__hook_lock_save_collection)

    def __hook_insert_origin_save(self, *args, **kwargs):
        instances = kwargs.get("instances", [])
        for instance in instances:
            if not isinstance(instance, ComponentDatalakeModel):
                continue
            instance.instance_id = self.instance_id
            instance.instance_type = self.managed_class.__name__

        return args, kwargs

    def __hook_insert_origin_save_dataframe(self, *args, **kwargs):
        dataframe = kwargs.get("dataframe")
        dataframe["instance_id"] = self.instance_id
        dataframe["instance_type"] = self.managed_class.__name__
        kwargs["dataframe"] = dataframe
        return args, kwargs

    def __hook_lock_save_collection(self, *args, **kwargs):
        kwargs["collection"] = self.collection_name
        return args, kwargs


class UtilsMixin:
    def get_history(self, **kwargs) -> pd.DataFrame:
        return self.datalake_client.get_dataframe(collection="default", **kwargs)

    def get_results(self, algorithm: Algorithm, output_model: ComponentDatalakeModel, **kwargs) -> pd.DataFrame:
        if output_model != getattr(algorithm.output_model, output_model.__name__):
            raise ValueError(
                f"Output model {output_model.__name__} does not match algorithm output"
            )

        return self.datalake_client.get_dataframe(
            collection=algorithm.collection,
            output_format=output_model.__name__,
            **kwargs
        )

    def save_results(self, output_model: ComponentDatalakeModel, dataframe: pd.DataFrame) -> None:
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


class BindingsMixin:
    def _load_client_bindings(self):
        self.communication_client.bind(EventNames.OPERATION_TRIGGER, self.__handle_operation_trigger)

    def __handle_operation_trigger(self, data: str):
        assert self.commands, "Please define .commands to start accepting request."
        operation_event = OperationTriggerEvent.parse_raw(data)
        operation: Operation = operation_event.data
        command: Command = operation.command
        try:
            command_function = getattr(self, command.name)
            command_kwargs_model = getattr(self.commands, command.name)
            parsed_command_kwargs = self.parse_parameters(command.dict()["fields"])
            command_kwargs = command_kwargs_model(**parsed_command_kwargs)
            # .to_dict is not keeping the models of subkeys
            command_kwargs = {
                str(field): getattr(command_kwargs, str(field)) for field in command_kwargs.__fields__
            }
            operation.response.return_value = str(command_function(**command_kwargs))
            operation.status = OperationStatus.SUCCESS
        except Exception as e:
            operation.response.error_detail = str(e)
            operation.status = OperationStatus.ERROR
        operation_callback_event = OperationUpdateEvent(data=operation)
        self.communication_client.trigger(operation_callback_event)


class ParametersMixin:
    def parse_parameters(self, parameters: List[Dict]) -> Dict:
        parameters = self._fetch_and_reload_component_objects_parameters(parameters)
        object_ids: Dict[str, Dict[str, List]] = self._get_object_ids(parameters)
        objects: Dict[str, BaseModel] = self._fetch_objects(object_ids)
        parameters = self._reload_parameters(parameters, objects=objects)
        transformed_parameters = self._transform_parameters(parameters)
        return transformed_parameters

    def _fetch_and_reload_component_objects_parameters(self, parameters: List[Dict]) -> List[Dict]:
        reloaded_parameters = []
        for raw_parameter in parameters:
            raw_parameter = raw_parameter.dict() if not isinstance(raw_parameter, dict) else raw_parameter
            parameter = raw_parameter.copy()
            type = parameter["type"]
            value = parameter["value"]
            multiple = parameter["multiple"]
            if type in NATIVE_TYPES or type in DATABASE_TYPES or type in STORAGE_TYPES:
                parameter["value"] = value
            else:
                object_ids = value if multiple else [value]
                objects = self.database_client.get(ComponentObject, id__in=object_ids)
                objects = [o.data for o in objects]
                parameter["value"] = [self._fetch_and_reload_component_objects_parameters(o) for o in objects] if multiple else self._fetch_and_reload_component_objects_parameters(objects[0])
            reloaded_parameters.append(parameter)
        return reloaded_parameters

    def _get_object_ids(self, parameters: List[Dict]) -> Dict[str, Dict[str, List]]:
        ids = {
            "database": defaultdict(list),
            "storage": defaultdict(list),
        }
        for parameter in parameters:
            parameter = parameter.dict() if not isinstance(parameter, dict) else parameter
            values = parameter["value"] if parameter["multiple"] else [parameter["value"]]
            if parameter["type"] in NATIVE_TYPES:
                continue
            elif parameter["type"] in DATABASE_TYPES:
                for value in values:
                    ids["database"][parameter["type"]].append(value)
            elif parameter["type"] in STORAGE_TYPES:
                for value in values:
                    ids["storage"][parameter["type"]].append(value)
            else:
                for value in values:
                    ids = merge(ids, self._get_object_ids(value), strategy=mergeStrategy.ADDITIVE)
        return ids

    def _fetch_objects(self, ids_to_fetch: Dict) -> Dict[str, BaseModel]:
        res: Dict = {
            None: None
        }
        for type, ids_ in ids_to_fetch["database"].items():
            objs = self.database_client.get(DATABASE_TYPES[type], id__in=ids_)
            res.update({obj.id: obj for obj in objs})

        for type, ids_ in ids_to_fetch["storage"].items():
            objs = self.storage_client.get(STORAGE_TYPES[type], id__in=ids_)
            res.update({obj.id: obj for obj in objs})
        return res

    def _reload_parameters(self, parameters: List[Dict], objects: Dict) -> List[Dict]:
        reloaded_parameters = []
        for raw_parameter in parameters:
            raw_parameter = raw_parameter.dict() if not isinstance(raw_parameter, dict) else raw_parameter
            parameter = raw_parameter.copy()
            type = parameter["type"]
            value = parameter["value"]
            multiple = parameter["multiple"]
            if type in NATIVE_TYPES:
                parameter["value"] = value
            elif type in DATABASE_TYPES or type in STORAGE_TYPES:
                parameter["value"] = [objects[val] for val in value] if multiple else objects[value]
            else:
                parameter["value"] = [self._reload_parameters(value, objects) for value in value] if multiple else self._reload_parameters(value, objects)
            reloaded_parameters.append(parameter)
        return reloaded_parameters

    def _transform_parameters(self, parameters: List[Dict]) -> Dict:
        parameters_dict: Dict = {}
        for parameter in parameters:
            type = parameter["type"]
            name = parameter["name"]
            value = parameter["value"]
            multiple = parameter["multiple"]

            if (value is [] or value == '') and type != "str":
                value = None

            if type in NATIVE_TYPES:
                parameters_dict[name] = value
            elif type in DATABASE_TYPES or type in STORAGE_TYPES:
                parameters_dict[name] = value
            else:
                parameters_dict[name] = [self._transform_parameters(val) for val in value] if multiple else self._transform_parameters(value)
        return parameters_dict


class AbstractComponent(RunnableMixin, HooksMixin, UtilsMixin, IndexMixin, BindingsMixin, ParametersMixin):
    collection_name = "default"
    managed_class: Type = None
    database_client_kwargs: Dict[str, Any] = {}
    datalake_client_kwargs: Dict[str, Any] = {}
    deployment_client_kwargs: Dict[str, Any] = {}
    storage_client_kwargs: Dict[str, Any] = {}
    communication_client_kwargs: Dict[str, Any] = {}

    def __init__(self, run_spec: dict, initial_setup: Optional[dict] = None, *args, **kwargs):
        self._spec: Deployment = Deployment(**run_spec)
        self._setup = default_setup
        if initial_setup:
            self._setup.configure(initial_setup)

        self.version: str = self._spec.version
        self.namespace = self._setup.settings.NAMESPACE
        self.instance_id = self._setup.settings.COMPONENT_ID

        self._load_instance_data()
        self._load_clients()
        self._load_spec_models()
        self._load_input_model()
        self._load_client_hooks()
        self._load_client_indexes()
        self._load_client_bindings()
        super().__init__(*args, **kwargs)  # This is calling RunnableMixin.init() only

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

    @abstractmethod
    def _load_instance_data(self):
        pass

    def _load_spec_models(self):
        self.output: Type = self._spec.output_model
        self.custom_types: Type = self._spec.custom_types_model
        self.commands: Type = self._spec.commands_model

    def _load_input_model(self):
        raw_spec = self.spec.dict()
        parsed_input_parameters = self.parse_parameters(raw_spec["input"])
        self.input: BaseModel = self._spec.input_model(**parsed_input_parameters)

    def _load_clients(self):
        self.database_client = self.setup.DATABASE_CLIENT(
            namespace=self.namespace,
            **self.database_client_kwargs
        )
        self.datalake_client = self.setup.DATALAKE_CLIENT(
            namespace=self.namespace,
            **self.datalake_client_kwargs
        )
        self.deployment_client = self.setup.DEPLOYMENT_CLIENT(
            namespace=self.namespace,
            **self.deployment_client_kwargs
        )
        self.storage_client = self.setup.STORAGE_CLIENT(
            namespace=self.namespace,
            **self.storage_client_kwargs
        )
        self.communication_client = self.setup.COMMUNICATION_CLIENT(
            namespace=self.namespace,
            **self.communication_client_kwargs
        )
        self.execution_client = ExecutionClient(namespace=self.namespace)
        self.blockchain_client = self.setup.BLOCKCHAIN_CLIENT(namespace=self.namespace)
