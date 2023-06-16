import re
import warnings
from datetime import datetime
from enum import auto
from typing import Any, ClassVar, Dict, List, Optional, Type

from pydantic import AnyUrl, BaseModel, PrivateAttr, create_model
from splight_lib.models.asset import Asset
from splight_lib.models.attribute import Attribute
from splight_lib.models.base import SplightDatabaseBaseModel
from splight_lib.models.exceptions import (
    InvalidComponentObjectInstance,
    SecretDecryptionError,
    SecretNotFound,
)
from splight_lib.models.file import File
from splight_lib.models.query import Query
from splight_lib.models.secret import Secret
from strenum import LowercaseStrEnum

warnings.filterwarnings("ignore", category=RuntimeWarning)


class PrivacyPolicy(LowercaseStrEnum):
    PUBLIC = auto()
    PRIVATE = auto()


class ComponentType(LowercaseStrEnum):
    ALGORITHM = auto()
    NETWORK = auto()
    CONNECTOR = auto()
    SIMULATOR = auto()
    OTHER = auto()


class Action(LowercaseStrEnum):
    READ = auto()
    WRITE = auto()
    READWRITE = auto()


class Parameter(BaseModel):
    name: str
    description: str = ""
    type: str = "str"
    required: bool = False
    multiple: bool = False
    sensitive: bool = False
    choices: Optional[List[Any]]
    depends_on: Optional[str]


class InputParameter(Parameter):
    value: Optional[Any] = None


class OutputParameter(BaseModel):
    name: str
    description: str = ""
    type: str
    choices: Optional[List[Any]] = None
    depends_on: Optional[str] = None
    filterable: bool = False


class Output(BaseModel):
    name: str
    fields: List[OutputParameter]


class CustomType(BaseModel):
    name: str
    action: Optional[Action]
    fields: List[Parameter]

    _reserved_names: ClassVar[List[str]] = ["id", "name", "description"]


class Command(BaseModel):
    name: str
    fields: List[InputParameter] = []


class Endpoint(BaseModel):
    name: Optional[str]
    port: str


class Binding(BaseModel):
    name: str
    object_type: str
    # TODO: Change to use EventAction from Communicaction
    object_action: str


class ComponentObject(SplightDatabaseBaseModel):
    id: Optional[str]
    name: str
    component_id: str
    description: Optional[str] = ""
    type: str
    data: List[InputParameter] = []


class Component(SplightDatabaseBaseModel):
    id: Optional[str]
    name: Optional[str]
    version: str
    custom_types: List[CustomType] = []
    component_type: ComponentType = ComponentType.CONNECTOR
    input: List[InputParameter] = []
    output: List[Output] = []
    commands: List[Command] = []
    endpoints: List[Endpoint] = []
    bindings: List[Binding] = []


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
    "Query": Query,
}

DB_MODEL_TYPE_MAPPING = {**NATIVE_TYPES, **DATABASE_TYPES}


def parse_variable_string(raw_value: Optional[str]) -> Any:
    if raw_value is None:
        return ""
    pattern = re.compile(r"^\$\{\{(\w+)\.(\w+)\}\}$")
    match = pattern.search(raw_value)
    if not match:
        return raw_value
    class_key, secret_name = match.groups()
    secret = Secret.list(name=secret_name, first=True)
    if not secret:
        raise SecretNotFound(secret_name)

    try:
        value = secret[0].decrypt()
    except Exception as exc:
        raise SecretDecryptionError() from exc
    return value


def get_field_value(field: InputParameter):
    multiple = field.multiple

    value = field.value
    if field.type in NATIVE_TYPES:
        value = (
            field.value
            if not isinstance(field.value, str)
            else parse_variable_string(field.value)
        )
    elif field.type in DATABASE_TYPES:
        model_class = DATABASE_TYPES[field.type]
        value = (
            model_class.retrieve(field.value)
            if not multiple
            else [model_class.retrieve(item) for item in field.value]
        )
    else:
        value_as_list = (
            ComponentObject.list(id__in=field.value)
            if multiple
            else [ComponentObject.retrieve(field.value)]
        )
        model_class = ComponentObjectInstance.from_component_object(
            value_as_list[0]
        )
        value_as_list = [
            model_class.parse_component_object(instance)
            for instance in value_as_list
        ]
        value = value_as_list if multiple else value_as_list[0]
    return value


class ComponentObjectInstance(SplightDatabaseBaseModel):
    id: Optional[str]
    name: str = ""
    description: Optional[str]

    _default_attrs: List[str] = PrivateAttr(
        ["id", "name", "component_id", "description"]
    )
    _schema: ClassVar[Optional[CustomType]] = None
    _component_id: ClassVar[Optional[str]] = None

    def save(self):
        component_obj = self.to_component_object()
        component_obj.save()
        if not self.id:
            self.id = component_obj.id

    def delete(self):
        component_obj = self.to_component_object()
        component_obj.delete()

    @classmethod
    def list(cls, **params: Dict) -> List["ComponentObjectInstance"]:
        if not cls._schema or not cls._component_id:
            raise InvalidComponentObjectInstance(
                (
                    "Missing schema or component_id attributes in "
                    "ComponentObjectInstance"
                )
            )
        params.update(
            {"type": cls.__name__, "component_id": cls._component_id}
        )
        instances = ComponentObject.list(**params)
        return [cls.parse_component_object(instance) for instance in instances]

    @classmethod
    def retrieve(cls, resource_id: str) -> "ComponentObjectInstance":
        if not cls._schema or not cls._component_id:
            raise InvalidComponentObjectInstance(
                (
                    "Missing schema or component_id attributes in "
                    "ComponentObjectInstance"
                )
            )
        instance = ComponentObject.retrieve(resource_id)
        return cls.parse_component_object(instance)

    def to_component_object(self) -> ComponentObject:
        schema = self._schema
        parameters = [
            self._convert_to_input_parameter(field, getattr(self, field.name))
            for field in schema.fields
        ]
        instance = ComponentObject(
            id=self.id,
            name=self.name,
            component_id=self._component_id,
            description=self.description,
            type=self.__class__.__name__,
            data=parameters,
        )
        return instance

    @staticmethod
    def _convert_to_input_parameter(
        field: Parameter, field_value: Any
    ) -> InputParameter:
        value = field_value
        if field.type not in NATIVE_TYPES:
            value = (
                [item.id for item in field_value]
                if field.multiple
                else field_value.id
            )
        parameter = field.dict()
        parameter.update({"value": value})
        return InputParameter.parse_obj(parameter)

    @classmethod
    def from_custom_type(
        cls,
        custom_type: CustomType,
        component_id: Optional[str] = None,
    ) -> Type["ComponentObjectInstance"]:
        fields = {}
        for field in custom_type.fields:
            field_type = DB_MODEL_TYPE_MAPPING.get(field.type, cls)
            field_type = List[field_type] if field.multiple else field_type
            fields.update({field.name: (field_type, ...)})
        fields.update(
            {
                "_schema": (
                    ClassVar[Optional[CustomType]],
                    custom_type,
                ),
                "_component_id": (ClassVar[Optional[str]], component_id),
            }
        )
        model_class = create_model(custom_type.name, **fields, __base__=cls)
        return model_class

    @classmethod
    def from_component_object(
        cls, instance: ComponentObject
    ) -> Type["ComponentObjectInstance"]:
        instance_dict = instance.dict()
        instance_dict["fields"] = instance_dict.pop("data")
        instance_dict["name"] = instance_dict.pop("type")
        return cls.from_custom_type(
            CustomType.parse_obj(instance_dict), instance.component_id
        )

    @classmethod
    def parse_component_object(
        cls, instance: ComponentObject
    ) -> "ComponentObjectInstance":
        params_dict = {
            field.name: get_field_value(field) for field in instance.data
        }
        params_dict.update(
            {
                "id": instance.id,
                "name": instance.name,
                "description": instance.description,
            }
        )
        return cls.parse_obj(params_dict)
