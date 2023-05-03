import re
import sys
import time
import uuid
from abc import abstractmethod
from collections import defaultdict
from functools import cached_property, partial
from tempfile import NamedTemporaryFile
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union
from retry import retry

import splight_models as spmodels
from mergedeep import Strategy as mergeStrategy
from mergedeep import merge
from pydantic import BaseModel, main
from splight_lib.execution import ExecutionClient, Thread
from splight_lib.logging._internal import LogTags, get_splight_logger
from splight_lib.settings import setup as default_setup
from splight_models import (
    Binding,
    Boolean,
    Command,
    CommunicationEvent,
    Component,
    ComponentCommandTriggerEvent,
    ComponentCommandUpdateEvent,
    ComponentObject,
    CustomType,
    DatalakeModel,
    Deployment,
    EventNames,
    Number,
    Secret,
    String,
)
from splight_models.component import (
    DATABASE_TYPES,
    NATIVE_TYPES,
    ComponentCommand,
    ComponentCommandStatus,
    InputParameter,
)
from splight_models.setpoint import (
    SetPoint,
    SetPointCreateEvent,
    SetPointResponse,
    SetPointResponseStatus,
    SetPointUpdateEvent,
)
from remote_splight_lib.auth import SplightAuthToken
from splight_lib.restclient import (
    ConnectError,
    HTTPError,
    SplightRestClient,
    Timeout,
)
from splight_lib.client.settings import settings_remote

logger = get_splight_logger()
REQUEST_EXCEPTIONS = (HTTPError, Timeout, ConnectError)


class SecretValueParser:
    def __init__(self, utils, *args, **kwargs):
        self.utils = utils

    def get_value(self, name: str) -> Any:
        logger.info("Obtaining secret: %s", name, tags=LogTags.SECRET)
        secret = self.utils.database_client.get(Secret, name=name, first=True)
        return secret.decrypt()


class VariableValueMixin:
    _variable_parameter_map_class = {
        "SECRET": SecretValueParser,
    }

    def parse_variable_string(self, value: str) -> Any:
        if value is None:
            return ""
        pattern = re.compile(r"^\$\{\{(\w+)\.(\w+)\}\}$")
        match = pattern.search(value)
        if not match:
            return value
        class_key, name = match.groups()
        try:
            parser_class = self._variable_parameter_map_class[class_key]
        except KeyError as e:
            raise NotImplementedError(
                f"Variable {class_key} is not supported yet."
            ) from e

        return parser_class(utils=self).get_value(name)


class RunnableMixin:
    healthcheck_interval = 5
    _HEALTH_FILE_PREFIX = "healthy_"
    _STARTUP_FILE_PREFIX = "ready_"

    def __init__(self):
        self.health_file = NamedTemporaryFile(prefix=self._HEALTH_FILE_PREFIX)
        self.startup_file = NamedTemporaryFile(
            prefix=self._STARTUP_FILE_PREFIX
        )
        logger.info(
            "Healthcheck file at: %s",
            self.health_file.name,
            tags=LogTags.RUNTIME,
        )
        logger.info(
            "Startup file at: %s", self.startup_file.name, tags=LogTags.RUNTIME
        )

        self.execution_client.start(Thread(self.healthcheck))

    def healthcheck(self) -> None:
        self.terminated = False
        while not self.terminated:
            if not self.execution_client.healthcheck():
                logger.error("Healthcheck task failed.", tags=LogTags.RUNTIME)
                self.health_file.close()
                logger.error(
                    "Healthcheck file removed: %s",
                    self.health_file,
                    tags=LogTags.RUNTIME,
                )
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
        collections: List[str] = self.__get_collections()
        for col in collections:
            logger.info(
                "Adding indexes: %s for collection %s",
                indexes,
                col,
                tags=LogTags.INDEX,
            )
            self.datalake_client.create_index(col, indexes)

    def __get_collections(self) -> List[str]:
        native_output_types = [Boolean, String, Number]
        # TODO do this autodiscovery better
        component_output_types = [
            v
            for v in self.output.__dict__.values()
            if isinstance(v, main.ModelMetaclass)
        ]
        return [
            r.Meta.collection_name
            for r in native_output_types + component_output_types
        ]

    def __get_indexes(self) -> List[Tuple[str, int]]:
        # order in indexes matters
        indexes: List[Tuple[str, int]] = [
            ("output_format", 1),
            ("instance_id", 1),
            ("instance_type", 1),
            ("asset", 1),
            ("attribute", 1),
            ("timestamp", -1),
        ]
        unique_indexes: Set[str] = set()

        for output in self._spec.output:
            for field in output.fields:
                if field.filterable:
                    unique_indexes.add(field.name)

        for index in unique_indexes:
            indexes.append((index, 1))

        return indexes


class HooksMixin:
    def _load_client_hooks(self):
        logger.info(
            "Adding pre-hooks for database and datalake clients.",
            tags=LogTags.HOOK,
        )

        # Datalake
        self.datalake_client.add_pre_hook(
            "save", self.__hook_insert_origin_save
        )
        self.datalake_client.add_pre_hook(
            "save_dataframe", self.__hook_insert_origin_save_dataframe
        )
        # Database
        self.database_client.add_pre_hook(
            "save", self.__hook_transform_from_custom_instances
        )
        self.database_client.add_pre_hook(
            "_get", self.__hook_transform_from_custom_resource_type
        )
        self.database_client.add_pre_hook(
            "delete", self.__hook_transform_from_custom_resource_type
        )
        self.database_client.add_pre_hook(
            "count", self.__hook_transform_from_custom_resource_type
        )
        self.database_client.add_post_hook(
            "_get", self.__hook_transform_to_custom_instances
        )
        self.database_client.add_post_hook(
            "save", self.__hook_transform_to_custom_instances
        )

    def __hook_insert_origin_save(self, *args, **kwargs):
        logger.info("Datalake save pre-hook.", tags=LogTags.HOOK)
        instances = kwargs.get("instances", [])
        for instance in instances:
            if not isinstance(instance, DatalakeModel):
                continue
            instance.instance_id = self.instance_id
            instance.instance_type = self.instance_type.__name__
        return args, kwargs

    def __hook_insert_origin_save_dataframe(self, *args, **kwargs):
        logger.info("Datalake dataframe save pre-hook.", tags=LogTags.HOOK)
        dataframe = kwargs.get("dataframe")
        dataframe["instance_id"] = self.instance_id
        dataframe["instance_type"] = self.instance_type.__name__
        kwargs["dataframe"] = dataframe
        return args, kwargs

    def __hook_transform_from_custom_resource_type(self, *args, **kwargs):
        logger.info("Transform from custom type pre-hook.", tags=LogTags.HOOK)
        resource_type = kwargs["resource_type"]
        if resource_type and hasattr(
            self.custom_types, resource_type.__name__
        ):
            kwargs["resource_type"] = ComponentObject
            kwargs["component_id"] = self.instance_id
            kwargs["type"] = resource_type.__name__
        return args, kwargs

    def __hook_transform_from_custom_instances(self, *args, **kwargs):
        logger.info(
            "Transform from custom instances pre-hook.", tags=LogTags.HOOK
        )
        instance = kwargs["instance"]
        if getattr(self.custom_types, type(instance).__name__, None):
            parsed_instance = ComponentObject(
                component_id=self.instance_id,
                type=type(instance).__name__,
                **self.unparse_parameters(instance),
            )
            kwargs["instance"] = parsed_instance
        return args, kwargs

    def __hook_transform_to_custom_instances(
        self, result: Union[BaseModel, List[BaseModel]]
    ):
        logger.info(
            "Transform to custom instances pre-hook.", tags=LogTags.HOOK
        )
        parsed_result = []
        convert_to_list = not isinstance(result, list)
        result = [result] if convert_to_list else result
        for object in result:
            if isinstance(object, ComponentObject):
                custom_object_data: List[InputParameter] = object.data
                custom_object_data.extend(
                    [
                        InputParameter(name=key, value=getattr(object, key))
                        for key in CustomType._reserved_names
                    ]
                )
                custom_object_model = getattr(self.custom_types, object.type)
                parsed_component_object = self.parse_parameters(
                    custom_object_data
                )
                object = custom_object_model(**parsed_component_object)
            parsed_result.append(object)

        parsed_result = parsed_result[0] if convert_to_list else parsed_result
        return parsed_result


class BindingsMixin:
    def _load_client_bindings(self):
        # Commands
        self.communication_client.bind(
            EventNames.COMPONENT_COMMAND_TRIGGER,
            self.__handle_component_command_trigger,
        )

        # Bindings
        for binding in self.bindings:
            binding_function = getattr(self, binding.name)
            binding_model = getattr(
                spmodels, binding.object_type, ComponentObject
            )
            binding_event_name = binding_model.get_event_name(
                binding.object_type, binding.object_action
            )
            logger.info(
                "Binding event: %s.", binding_event_name, tags=LogTags.BINDING
            )
            binding_handler = self.__handle_native_object_trigger
            if binding_model == ComponentObject:
                binding_handler = self.__handle_component_object_trigger
            if binding_model == SetPoint:
                binding_handler = self.__handle_setpoint_trigger

            self.communication_client.bind(
                binding_event_name,
                partial(
                    binding_handler, binding_function, binding.object_type
                ),
            )
            logger.info(
                "Binded event: %s", binding_event_name, tags=LogTags.BINDING
            )

    def __handle_setpoint_trigger(
        self, binding_function: Callable, binding_object_type: str, data: str
    ):
        try:
            logger.debug("Setpoint triggered.", tags=LogTags.SETPOINT)
            object_event = SetPointCreateEvent.parse_raw(data)
            setpoint = object_event.data
            response_status = SetPointResponseStatus(
                binding_function(setpoint)
            )
            if response_status == SetPointResponseStatus.IGNORE:
                return

            setpoint.responses = [
                SetPointResponse(
                    component=self.instance_id,
                    status=response_status,
                )
            ]
            setpoint_callback_event = SetPointUpdateEvent(data=setpoint)
            self.communication_client.trigger(setpoint_callback_event)
        except Exception as e:
            logger.error(
                "Error while handling setpoint create: %s",
                e,
                exc_info=True,
                tags=LogTags.SETPOINT,
            )

    def __handle_native_object_trigger(
        self, binding_function: Callable, binding_object_type: str, data: str
    ):
        assert self.bindings, "Please define .bindings to start."
        try:
            logger.info(
                "Binding for native object of type %s triggered.",
                binding_object_type,
                tags=LogTags.BINDING,
            )
            object_event = CommunicationEvent.parse_raw(data)
            object_model = getattr(spmodels, binding_object_type)
            binding_kwargs = object_model(**object_event.data)
            binding_function(binding_kwargs)
        except Exception as e:
            logger.error(
                "Error while handling native object trigger: %s",
                e,
                exc_info=True,
                tags=LogTags.BINDING,
            )

    def __handle_component_object_trigger(
        self, binding_function: Callable, binding_object_type: str, data: str
    ):
        assert self.bindings, "Please define .bindings to start."
        logger.info(
            "Binding for component object of type %s triggered.",
            binding_object_type,
            tags=LogTags.BINDING,
        )
        component_object_event = CommunicationEvent.parse_raw(data)
        component_object: ComponentObject = ComponentObject(
            **component_object_event.data
        )
        custom_object_data = component_object.data
        custom_object_data.extend(
            [
                InputParameter(name=key, value=getattr(component_object, key))
                for key in CustomType._reserved_names
            ]
        )
        custom_object_model = getattr(self.custom_types, binding_object_type)
        parsed_component_object = self.parse_parameters(custom_object_data)
        binding_kwargs = custom_object_model(**parsed_component_object)
        binding_function(binding_kwargs)

    def __handle_component_command_trigger(self, data: str):
        assert (
            self.commands
        ), "Please define .commands to start accepting request."
        component_command_event = ComponentCommandTriggerEvent.parse_raw(data)
        component_command: ComponentCommand = component_command_event.data
        command: Command = component_command.command
        logger.info(
            "Binding for component command '%s' triggered.",
            command.name,
            tags=LogTags.COMMAND,
        )
        try:
            command_function = getattr(self, command.name)
            command_kwargs_model = getattr(self.commands, command.name)
            parsed_command_kwargs = self.parse_parameters(
                command.dict()["fields"]
            )
            command_kwargs = command_kwargs_model(**parsed_command_kwargs)
            # .dict is not keeping the models of subkeys
            command_kwargs = {
                str(field): getattr(command_kwargs, str(field))
                for field in command_kwargs.__fields__
            }
            component_command.response.return_value = str(
                command_function(**command_kwargs)
            )
            component_command.status = ComponentCommandStatus.SUCCESS
        except Exception as e:
            logger.error(
                "Error while handling component command trigger: %s",
                e,
                exc_info=True,
                tags=LogTags.COMMAND,
            )
            component_command.response.error_detail = str(e)
            component_command.status = ComponentCommandStatus.ERROR
        component_command_callback_event = ComponentCommandUpdateEvent(
            data=component_command
        )
        self.communication_client.trigger(component_command_callback_event)


class ParametersMixin:
    def unparse_parameters(self, instance: Dict) -> List[Dict]:
        logger.debug(
            "Unparsing parameters for an instance of %s",
            type(instance).__name__,
            tags=LogTags.PARAMETER,
        )
        custom_type = getattr(self.custom_types, type(instance).__name__, None)
        if custom_type is None:
            raise NotImplementedError
        reserved_parameters = {
            k: v
            for k, v in instance.dict().items()
            if k in CustomType._reserved_names
        }
        custom_parameters = {
            k: v
            for k, v in instance.dict().items()
            if k not in CustomType._reserved_names
        }
        fields = []
        for key, obj in custom_parameters.items():
            field = getattr(custom_type.SpecFields, key)
            if field is None:
                continue
            value = obj

            if field.type not in NATIVE_TYPES:
                value = [o["id"] for o in obj] if field.multiple else obj["id"]

            fields.append(
                InputParameter(
                    name=field.name,
                    value=value,
                    type=field.type,
                    multiple=field.multiple,
                    required=field.required,
                    choices=field.choices,
                    depends_on=field.depends_on,
                    sensitive=field.sensitive,
                )
            )
        return {"data": fields, **reserved_parameters}

    def parse_parameters(self, parameters: List[Dict]) -> Dict:
        logger.debug(
            "Parsing parameters %s", parameters, tags=LogTags.PARAMETER
        )
        parameters = self._fetch_and_reload_component_objects_parameters(
            parameters
        )
        object_ids: Dict[str, Dict[str, List]] = self._get_object_ids(
            parameters
        )
        objects: Dict[str, BaseModel] = self._fetch_objects(object_ids)
        parameters = self._reload_parameters(parameters, objects=objects)
        transformed_parameters = self._transform_parameters(parameters)
        return transformed_parameters

    def _fetch_and_reload_component_objects_parameters(
        self, parameters: List[Dict]
    ) -> List[Dict]:
        reloaded_parameters = []
        for raw_parameter in parameters:
            raw_parameter = (
                raw_parameter.dict()
                if not isinstance(raw_parameter, dict)
                else raw_parameter
            )
            parameter = raw_parameter.copy()
            type = parameter["type"]
            value = parameter["value"]
            multiple = parameter["multiple"]
            if type == "str":
                parameter["value"] = self.parse_variable_string(value)
            if type in NATIVE_TYPES or type in DATABASE_TYPES:
                parameter["value"] = value
            else:
                object_ids = value if multiple else [value]
                objects = (
                    self.database_client.get(
                        ComponentObject, id__in=object_ids, ignore_hook=True
                    )
                    if object_ids
                    else []  # TODO: Investigate why the filter is not working properly.
                )
                for o in objects:
                    component_object_data = [
                        InputParameter(name=key, value=getattr(o, key))
                        for key in CustomType._reserved_names
                    ]
                    o.data.extend(component_object_data)
                objects = [o.data for o in objects]
                parameter["value"] = (
                    [
                        self._fetch_and_reload_component_objects_parameters(o)
                        for o in objects
                    ]
                    if multiple
                    else self._fetch_and_reload_component_objects_parameters(
                        objects[0]
                    )
                )
            reloaded_parameters.append(parameter)
        return reloaded_parameters

    def _get_object_ids(
        self, parameters: List[Dict]
    ) -> Dict[str, Dict[str, List]]:
        ids = {"database": defaultdict(list)}
        for parameter in parameters:
            parameter = (
                parameter.dict()
                if not isinstance(parameter, dict)
                else parameter
            )
            if parameter["value"] is None:
                continue
            values = (
                parameter["value"]
                if parameter["multiple"]
                else [parameter["value"]]
            )
            if parameter["type"] in NATIVE_TYPES:
                continue
            elif parameter["type"] in DATABASE_TYPES:
                for value in values:
                    ids["database"][parameter["type"]].append(value)
            else:
                for value in values:
                    ids = merge(
                        ids,
                        self._get_object_ids(value),
                        strategy=mergeStrategy.ADDITIVE,
                    )
        return ids

    def _fetch_objects(self, ids_to_fetch: Dict) -> Dict[str, BaseModel]:
        res: Dict = {None: None}
        for type, ids_ in ids_to_fetch["database"].items():
            objs = self.database_client.get(DATABASE_TYPES[type], id__in=ids_)
            res.update({obj.id: obj for obj in objs})
        return res

    def _reload_parameters(
        self, parameters: List[Dict], objects: Dict
    ) -> List[Dict]:
        reloaded_parameters = []
        for raw_parameter in parameters:
            raw_parameter = (
                raw_parameter.dict()
                if not isinstance(raw_parameter, dict)
                else raw_parameter
            )
            parameter = raw_parameter.copy()
            type = parameter["type"]
            value = parameter["value"]
            multiple = parameter["multiple"]
            if type == "str":
                parameter["value"] = self.parse_variable_string(value)
            elif type in NATIVE_TYPES or value is None:
                parameter["value"] = value
            elif type in DATABASE_TYPES:
                parameter["value"] = (
                    [objects[val] for val in value]
                    if multiple
                    else objects[value]
                )
            else:
                parameter["value"] = (
                    [
                        self._reload_parameters(value, objects)
                        for value in value
                    ]
                    if multiple
                    else self._reload_parameters(value, objects)
                )
            reloaded_parameters.append(parameter)
        return reloaded_parameters

    def _transform_parameters(self, parameters: List[Dict]) -> Dict:
        parameters_dict: Dict = {}
        for parameter in parameters:
            type = parameter["type"]
            name = parameter["name"]
            value = parameter["value"]
            multiple = parameter["multiple"]

            if (value is [] or value == "") and type != "str":
                value = None

            if type in NATIVE_TYPES:
                parameters_dict[name] = value
            elif type in DATABASE_TYPES:
                parameters_dict[name] = value
            else:
                parameters_dict[name] = (
                    [self._transform_parameters(val) for val in value]
                    if multiple
                    else self._transform_parameters(value)
                )
        return parameters_dict


class DuplicatedComponentException(Exception):
    pass


class AbstractComponent(
    RunnableMixin,
    HooksMixin,
    IndexMixin,
    BindingsMixin,
    ParametersMixin,
    VariableValueMixin,
):
    database_client_kwargs: Dict[str, Any] = {}
    datalake_client_kwargs: Dict[str, Any] = {}
    deployment_client_kwargs: Dict[str, Any] = {}
    communication_client_kwargs: Dict[str, Any] = {}
    blockchain_client_kwargs: Dict[str, Any] = {}

    def __init__(
        self,
        run_spec: dict,
        initial_setup: Optional[dict] = None,
        component_id: str = None,
        *args,
        **kwargs,
    ):
        self._setup = default_setup
        if initial_setup:
            self._setup.configure(initial_setup)

        self.namespace = self._setup.settings.NAMESPACE
        self.instance_type = Component
        self.instance_id = component_id if component_id else str(uuid.uuid4())
        self.deployment_id = run_spec.pop("id", None)

        self._spec: Deployment = Deployment(id=self.instance_id, **run_spec)
        self._check_duplicated_component()
        self._load_instance_kwargs_for_clients()
        self._load_clients(
            database_config=kwargs.get("database_config", {}),
            datalake_config=kwargs.get("datalake_config", {}),
        )
        self._load_spec_models()
        self._load_input_model()
        self._load_client_indexes()
        self._load_client_hooks()
        self._load_client_bindings()
        super().__init__()  # This is calling RunnableMixin.init() only

    @property
    def spec(self) -> Deployment:
        return self._spec

    @property
    def setup(self):
        return self._setup

    @cached_property
    def instance(self):
        return self.database_client.get(
            resource_type=self.instance_type, id=self.instance_id, first=True
        )

    def _load_instance_kwargs_for_clients(self):
        self.communication_client_kwargs["instance_id"] = self.instance_id

    def _load_spec_models(self):
        self.output: Type = self._spec.output_model
        self.custom_types: Type = self._spec.custom_types_model
        self.commands: Type = self._spec.commands_model
        self.bindings: List[Binding] = self._spec.bindings

    def _load_input_model(self):
        raw_spec = self.spec.dict()
        parsed_input_parameters = self.parse_parameters(raw_spec["input"])
        self.input: BaseModel = self._spec.input_model(
            **parsed_input_parameters
        )

    def _load_clients(self, database_config: Dict, datalake_config: Dict):
        self.database_client = self.setup.DATABASE_CLIENT(
            namespace=self.namespace, **database_config
        )
        self.datalake_client = self.setup.DATALAKE_CLIENT(
            namespace=self.namespace, **datalake_config
        )
        self.communication_client = self.setup.COMMUNICATION_CLIENT(
            namespace=self.namespace, **self.communication_client_kwargs
        )
        self.execution_client = ExecutionClient(namespace=self.namespace)

    @retry(REQUEST_EXCEPTIONS, tries=3, delay=2, jitter=1)
    def _check_duplicated_component(self):
        """
            Validates that there are no other connections to communication client
        """
        token = SplightAuthToken(
            access_key=settings_remote.SPLIGHT_ACCESS_ID,
            secret_key=settings_remote.SPLIGHT_SECRET_KEY,
        )
        rest_client = SplightRestClient()
        rest_client.update_headers(token.header)
        api_url = f"{settings_remote.SPLIGHT_PLATFORM_API_HOST}/v2/engine/component/components/{self.instance_id}/connections/"
        response = rest_client.get(api_url)
        if response.status_code == 200:
            connections = response.json()['subscription_count']
            if int(connections) > 0:
                raise DuplicatedComponentException(
                    f"Component with id {self.instance_id} is already running."
                )
        else:
            raise Exception(
                f"Error checking if component is already running. Status: {response.status_code}"
            )
