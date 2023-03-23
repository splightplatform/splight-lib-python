from splight_models.constants import (
    ComponentSize,
    RestartPolicy,
    LogginLevel,
    ComponentStatus,
    ComponentType
)
from splight_models.asset import Asset
from splight_models.attribute import Attribute
from splight_models.base import SplightBaseModel
from splight_models.file import File
from splight_models.datalake import DatalakeModel
from splight_models.graph import Graph
from splight_models.query import Query
from splight_models import EventActions, EventNames, CommunicationEvent
from datetime import datetime
from enum import Enum, auto
from typing import Type, List, Dict, Tuple, Optional, Any, Union
from pydantic import BaseModel, create_model, Field, AnyUrl, ValidationError, validator
from copy import copy
from functools import cached_property
import inspect
from strenum import LowercaseStrEnum


def choices_validator(cls, value, field):
    parameter = getattr(cls.SpecFields, field.name, None)
    if parameter is None:
        return value

    valid_choices = parameter.choices
    if value not in valid_choices:
        raise ValidationError(f"{field.name} value not in valid choices.")
    return value


class Action(LowercaseStrEnum):
    READ = auto()
    WRITE = auto()
    READWRITE = auto()


class Parameter(SplightBaseModel):
    name: str
    description: str = ''
    type: str = "str"
    required: bool = False
    multiple: bool = False
    sensitive: bool = False
    choices: Optional[List[Any]] = None
    depends_on: Optional[str] = None


class InputParameter(Parameter):
    value: Optional[Any] = None


class OutputParameter(SplightBaseModel):
    name: str
    description: str = ''
    type: str
    choices: Optional[List[Any]] = None
    depends_on: Optional[str] = None
    filterable: bool = False


class CommandParameter(InputParameter):
    pass


class CustomType(SplightBaseModel):
    _reserved_names = ["id", "name", "description"]
    name: str
    action: Optional[Action] = None
    fields: List[Parameter]


class Output(SplightBaseModel):
    name: str
    fields: List[OutputParameter]


class Command(SplightBaseModel):
    name: str
    fields: List[CommandParameter]


class Endpoint(SplightBaseModel):
    name: Optional[str]
    port: str


class Binding(SplightBaseModel):
    name: str
    object_type: str
    object_action: EventActions


class ComponentObject(SplightBaseModel):
    id: Optional[str]
    component_id: str
    name: str
    description: Optional[str]
    type: str
    data: List[InputParameter]


class ComponentCommandResponse(SplightBaseModel):
    return_value: Optional[str] = None
    error_detail: Optional[str] = None


class ComponentCommandStatus(str, Enum):
    NOT_SENT = "not_sent"
    PENDING = "pending"
    SUCCESS = "succeeded"
    ERROR = "error"


class ComponentCommand(SplightBaseModel):
    id: Optional[str]
    command: Command
    status: ComponentCommandStatus
    response: ComponentCommandResponse = ComponentCommandResponse()

    def get_event_name(self, action: EventActions) -> str:
        return f"componentcommand_{action}"


class ComponentCommandTriggerEvent(CommunicationEvent):
    event_name: str = Field(EventNames.COMPONENT_COMMAND_TRIGGER, const=True)
    data: ComponentCommand


class ComponentCommandCreateEvent(CommunicationEvent):
    event_name: str = Field(EventNames.COMPONENT_COMMAND_CREATE, const=True)
    data: ComponentCommand


class ComponentCommandUpdateEvent(CommunicationEvent):
    event_name: str = Field(EventNames.COMPONENT_COMMAND_UPDATE, const=True)
    data: ComponentCommand


class BaseComponent(SplightBaseModel):
    id: Optional[str]
    name: Optional[str] = None
    version: str
    custom_types: Optional[List[CustomType]] = []
    component_type: Optional[ComponentType]
    input: Optional[List[InputParameter]] = []
    output: Optional[List[Output]] = []
    commands: Optional[List[Command]] = []
    endpoints: Optional[List[Endpoint]] = []
    bindings: Optional[List[Binding]] = []

    class Config:
        keep_untouched = (cached_property,)

    @cached_property
    def custom_types_model(self) -> Type:
        return ComponentModelsFactory(
            component_id=self.id
        ).get_custom_types_model(self.custom_types)

    @cached_property
    def input_model(self) -> Type:
        custom_type_model = self.custom_types_model
        custom_types = inspect.getmembers(custom_type_model)
        custom_types_dict = {a[0]: a[1] for a in custom_types if not a[0].startswith('__')}
        return ComponentModelsFactory(
            type_map=custom_types_dict,
            component_id=self.id
        ).get_input_model(self.input)

    @cached_property
    def output_model(self) -> Type:
        return ComponentModelsFactory(
            component_id=self.id
        ).get_output_model(self.output)

    @cached_property
    def commands_model(self) -> Type:
        custom_type_model = self.custom_types_model
        custom_types = inspect.getmembers(custom_type_model)
        custom_types_dict = {a[0]: a[1] for a in custom_types if not a[0].startswith('__')}
        return ComponentModelsFactory(
            type_map=custom_types_dict,
            component_id=self.id
        ).get_commands_model(self.commands)


class Component(BaseComponent):
    id: Optional[str]
    description: Optional[str]
    log_level: LogginLevel = LogginLevel.info
    component_capacity: ComponentSize = ComponentSize.small
    restart_policy: RestartPolicy = RestartPolicy.ON_FAILURE
    status: ComponentStatus = ComponentStatus.STOPPED
    active: bool = False
    namespace: Optional[str] = None

    @property
    def service_name(self):
        return f"service-{self.id}"

    @property
    def secret_name(self):
        return f"{self.namespace}-secrets"


NATIVE_TYPES = {
    "int": int,
    "bool": bool,
    "str": str,
    "float": float,
    "datetime": datetime,
    "url": AnyUrl,
}

DATABASE_TYPES = {
    "Component": Component,
    "Asset": Asset,
    "Attribute": Attribute,
    "File": File,
    "Graph": Graph,
    "Query": Query,
}


SIMPLE_TYPES = list(NATIVE_TYPES.keys()) + list(DATABASE_TYPES.keys())


class ComponentModelsFactory:
    def __init__(self, type_map: Dict[str, Type] = {}, component_id: Optional[str] = None) -> None:
        self._component_id = component_id
        self._type_map = {
            **type_map,
            **self._load_type_map()
        }

    @staticmethod
    def _load_type_map() -> Dict[str, Type]:
        type_map: Dict[str, Type] = {}
        type_map.update(NATIVE_TYPES)
        type_map.update({k: Union[str, v] for k, v in DATABASE_TYPES.items()})
        return type_map

    def get_input_model(self, inputs: List) -> BaseModel:
        # There is only one input model. No need to define a dict
        return self._create_model("Input", inputs)

    def get_custom_types_model(self, custom_types: List) -> Type:
        custom_types_dict: Dict[str, BaseModel] = {}
        for custom_type in custom_types:
            custom_type.fields.extend(
                [
                    Parameter(name=key, value=None)
                    for key in CustomType._reserved_names
                ]
            )
            model = self._create_model(custom_type.name, custom_type.fields)
            custom_types_dict[custom_type.name] = model
            self._type_map[custom_type.name] = model

        return type("CustomTypes", (), custom_types_dict)

    def get_output_model(self, outputs: List) -> BaseModel:
        output_models: Dict[str, BaseModel] = {}

        for output in outputs:
            output_format_field = {
                "output_format": Field(output.name, const=True),
            }
            output_models[output.name] = self._create_model(output.name,
                                                            output.fields,
                                                            output_format_field,
                                                            DatalakeModel)

        return type("Output", (), output_models)

    def get_commands_model(self, commands: List) -> BaseModel:
        command_models: Dict[str, BaseModel] = {}
        for command in commands:
            command_models[command.name] = self._create_model(command.name,
                                                              command.fields)
        return type("Commands", (), command_models)

    def _create_model(self,
                      name: str,
                      fields: List[Parameter],
                      extra_fields: Dict = {},
                      base: Type = SplightBaseModel) -> Type:

        # Inline classes for meta attrs
        class SpecFields:
            pass

        class Meta:
            collection_name = str(self._component_id)

        fields_dict: Dict[str, Tuple] = copy(extra_fields)
        validators = {}
        for field in fields:
            setattr(SpecFields, field.name, field)
            type = self._type_map[field.type]
            choices = getattr(field, "choices", None)
            multiple = getattr(field, "multiple", False)
            required = getattr(field, "required", True)

            if choices:
                validators.update({
                    "choices_validator": validator(
                        field.name, pre=True, allow_reuse=True
                     )(choices_validator)
                })

            if multiple:
                type = List[type]

            value = ...
            if not required:
                type = Optional[type]
                value = None

            fields_dict[field.name] = (type, value)

        model = create_model(
            name, **fields_dict, __base__=base, __validators__=validators
        )
        model.SpecFields = SpecFields
        model.Meta = Meta
        return model
