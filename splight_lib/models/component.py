from datetime import datetime
from enum import auto
from typing import Any, Dict, List, Optional, Type, TypedDict

from pydantic import (
    AnyUrl,
    BaseModel,
    PrivateAttr,
    create_model_from_typeddict,
)
from strenum import LowercaseStrEnum

from splight_lib.models.asset import Asset
from splight_lib.models.attribute import Attribute
from splight_lib.models.base import SplightDatabaseBaseModel
from splight_lib.models.file import File
from splight_lib.models.query import Query


class ComponentType(LowercaseStrEnum):
    ALGORITHM = auto()
    NETWORK = auto()
    CONNECTOR = auto()
    SIMULATOR = auto()


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

TYPE_MAPPING = {**NATIVE_TYPES, **DATABASE_TYPES}


def get_field_value(field: InputParameter):
    # choices = field.choices
    multiple = field.multiple
    # required = field.required

    value = field.value
    if field.type in NATIVE_TYPES:
        value = field.value
    elif field.type in DATABASE_TYPES:
        model_class = DATABASE_TYPES[field.type]
        value = (
            model_class.retrieve(field.value)
            if not multiple
            else [model_class.retrieve(item) for item in field.value]
        )
    else:
        value = (
            ComponentObjectInstance.retrieve(field.value)
            if not multiple
            else [
                ComponentObjectInstance.retrieve(item) for item in field.value
            ]
        )
    return value


class ComponentObjectInstance(SplightDatabaseBaseModel):
    id: Optional[str]
    name: str = ""
    component_id: str
    description: Optional[str]

    _default_attrs: List[str] = PrivateAttr(
        ["id", "name", "component_id", "description"]
    )

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
        # TODO: Add param type always
        params.update({"type": cls.__name__})
        instances = ComponentObject.list(**params)
        return [cls.from_component_object(instance) for instance in instances]

    @classmethod
    def retrieve(cls, resource_id: str) -> "ComponentObjectInstance":
        instance = ComponentObject.retrieve(resource_id)
        return cls.from_component_object(instance)

    def to_component_object(self) -> ComponentObject:
        instance = ComponentObject(
            id=self.id,
            name=self.name,
            component_id=self.component_id,
            description=self.description,
            type=self.__class__.__name__,
            data=self._get_input_parameters(),
        )
        return instance

    def _get_input_parameters(self) -> List[InputParameter]:
        attributes = {
            name: value
            for name, value in self.__dict__.items()
            if name not in self._default_attrs
        }
        parameters = []
        for name, value in attributes.items():
            field = self.__fields__.get(name)
            multiple = False
            if isinstance(value, list):
                multiple = True

            param_type = (
                type(value[0]).__name__ if multiple else type(value).__name__
            )
            param_value = value
            if param_type not in NATIVE_TYPES:
                param_value = (
                    [item.id for item in value] if multiple else value.id
                )
            param = InputParameter(
                name=name,
                value=param_value,
                type=param_type,
                required=field.required,
                multiple=multiple,
            )
            parameters.append(param)
        return parameters

    # TODO: Check how to minimize call to this method
    @classmethod
    def model_class_from_component_object(
        cls, instance: ComponentObject
    ) -> Type["ComponentObjectInstance"]:
        fields = {}
        for field in instance.data:
            field_type = TYPE_MAPPING.get(field.type, cls)
            field_type = List[field_type] if field.multiple else field_type
            fields.update({field.name: field_type})
        model_class = create_model_from_typeddict(
            TypedDict(instance.type, fields), __base__=cls
        )
        return model_class

    @classmethod
    def from_component_object(
        cls, instance: ComponentObject
    ) -> "ComponentObjectInstance":
        model_class = cls.model_class_from_component_object(instance)
        params_dict = {
            field.name: get_field_value(field) for field in instance.data
        }
        params_dict.update(
            {
                "id": instance.id,
                "name": instance.name,
                "component_id": instance.component_id,
                "description": instance.description,
            }
        )
        return model_class.parse_obj(params_dict)
