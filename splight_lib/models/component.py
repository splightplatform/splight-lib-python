import re
import warnings
from abc import ABC, abstractmethod
from datetime import datetime
from enum import auto
from typing import Any, ClassVar, Dict, List, Optional, Type, Union

from pydantic import AnyUrl, BaseModel, Field, PrivateAttr, create_model
from strenum import LowercaseStrEnum

from splight_lib.models.asset import Asset
from splight_lib.models.attribute import Attribute
from splight_lib.models.base import SplightDatabaseBaseModel
from splight_lib.models.data_address import DataAddresses as DLDataAddress
from splight_lib.models.exceptions import (
    InvalidObjectInstance,
    SecretDecryptionError,
    SecretNotFound,
)
from splight_lib.models.file import File
from splight_lib.models.query import Query
from splight_lib.models.secret import Secret

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


class RoutineStatus(LowercaseStrEnum):
    RUNNING = auto()
    PENDING = auto()
    FAILED = auto()


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


class DataAdress(Parameter):
    choices: None = None
    depends_on: None = None
    required: bool = True
    type: str = Field("DataAdress", const=True)
    value_type: str = "Number"


class InputDataAdress(DataAdress):
    value: Union[List[Dict[str, str]], Dict[str, str]]


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
    fields: List[Parameter]

    _reserved_names: ClassVar[List[str]] = ["id", "name", "description"]


class Routine(BaseModel):
    name: str

    create_handler: Optional[str]
    update_handler: Optional[str]
    delete_handler: Optional[str]

    config: Optional[List[Parameter]] = []
    input: List[DataAdress] = []
    output: List[DataAdress] = []

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


class SplightObject(SplightDatabaseBaseModel):
    id: Optional[str]
    name: str
    component_id: str
    description: Optional[str] = ""
    type: str


class ComponentObject(SplightObject):
    data: List[InputParameter] = []


class RoutineObject(SplightObject):
    status: Optional[RoutineStatus] = RoutineStatus.RUNNING

    config: Optional[List[InputParameter]] = []
    input: List[InputDataAdress] = []
    output: List[InputDataAdress] = []


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
    routines: List[Routine] = []


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

DATALAKE_TYPES = {
    "DataAdress": DLDataAddress,
}

DB_MODEL_TYPE_MAPPING = {
    **NATIVE_TYPES,
    **DATABASE_TYPES,
    **DATALAKE_TYPES,
}


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


def get_field_value(field: Union[InputParameter, List[InputParameter]]):
    multiple = field.multiple

    value = field.value
    if not value:
        return [] if multiple else None

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
    elif field.type in DATALAKE_TYPES:
        model_class = DATALAKE_TYPES[field.type]
        value = field.value.copy()
        value = value if multiple else [value]
        for item in value:
            item.update({"type": field.value_type})

        value = [model_class.parse_obj(item) for item in value]
        value = value[0] if not multiple else value
    else:
        value_as_list = (
            ComponentObject.list(id__in=field.value)
            if multiple
            else [ComponentObject.retrieve(field.value)]
        )
        model_class = ComponentObjectInstance.from_object(value_as_list[0])
        value_as_list = [
            model_class.parse_object(instance) for instance in value_as_list
        ]
        value = value_as_list if multiple else value_as_list[0]
    return value


class AbstractObjectInstance(ABC, SplightDatabaseBaseModel):
    id: Optional[str]
    name: str = ""
    description: Optional[str]

    _default_attrs: List[str] = PrivateAttr(
        ["id", "name", "component_id", "description"]
    )
    _schema: ClassVar[Optional[BaseModel]] = None
    _database_class: ClassVar[Optional[Type[SplightDatabaseBaseModel]]] = None
    _component_id: ClassVar[Optional[str]] = None

    def save(self):
        component_obj = self.to_object()
        component_obj.save()
        if not self.id:
            self.id = component_obj.id

    def delete(self):
        component_obj = self.to_object()
        component_obj.delete()

    @classmethod
    def list(cls, **params: Dict) -> List["AbstractObjectInstance"]:
        if not cls._schema or not cls._component_id:
            raise InvalidObjectInstance(
                (
                    "Missing schema or component_id attributes in "
                    f"{cls.__name__}"
                )
            )
        params.update(
            {"type": cls.__name__, "component_id": cls._component_id}
        )
        instances = cls._database_class.list(**params)
        return [cls.parse_object(instance) for instance in instances]

    @classmethod
    def retrieve(cls, resource_id: str) -> "AbstractObjectInstance":
        if not cls._schema or not cls._component_id:
            raise InvalidObjectInstance(
                (
                    "Missing schema or component_id attributes in "
                    f"{cls.__name__}"
                )
            )
        instance = cls._database_class.retrieve(resource_id)
        return cls.parse_object(instance)

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

    @staticmethod
    def _convert_to_input_data_addres(
        field: DataAdress, field_value: Any
    ) -> InputDataAdress:
        if field.multiple:
            value = [
                {
                    "asset": item.asset,
                    "attribute": item.attribute,
                }
                for item in field_value
            ]
        else:
            value = {
                "asset": field_value.asset,
                "attribute": field_value.attribute,
            }
        parameter = field.dict()
        parameter.update({"value": value})
        return InputDataAdress.parse_obj(parameter)

    @abstractmethod
    def to_object(self) -> SplightObject:
        """
        Returns a databas object
        """
        pass

    @classmethod
    @abstractmethod
    def parse_object(
        cls, component_object: SplightObject
    ) -> "AbstractObjectInstance":
        """
        Returns a new instance of the subclass of AbstractObjectInstance
        """
        pass

    @classmethod
    @abstractmethod
    def from_object(
        cls, instance: SplightObject
    ) -> Type["AbstractObjectInstance"]:
        """
        Return the constructor subclass of AbstractObjectInstance
        """
        pass


class ComponentObjectInstance(AbstractObjectInstance):
    _schema: ClassVar[Optional[CustomType]] = None
    _database_class: ClassVar[Type[SplightDatabaseBaseModel]] = ComponentObject

    def to_object(self) -> ComponentObject:
        schema = self._schema

        data = [
            self._convert_to_input_parameter(field, getattr(self, field.name))
            for field in schema.fields
        ]

        instance = ComponentObject(
            id=self.id,
            name=self.name,
            component_id=self._component_id,
            description=self.description,
            type=self.__class__.__name__,
            data=data,
        )
        return instance

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
            field_type = (
                Optional[field_type] if not field.required else field_type
            )
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
    def from_object(
        cls, instance: ComponentObject
    ) -> Type["ComponentObjectInstance"]:
        instance_dict = instance.dict()
        instance_dict["fields"] = instance_dict.pop("data")
        instance_dict["name"] = instance_dict.pop("type")
        return cls.from_custom_type(
            CustomType.parse_obj(instance_dict), instance.component_id
        )

    @classmethod
    def parse_object(
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

    @classmethod
    def from_component(
        cls,
        component: Component,
    ) -> Dict[str, "ComponentObjectInstance"]:
        return {
            ct.name: cls.from_custom_type(ct, component.id)
            for ct in component.custom_types
        }


class RoutineObjectInstance(AbstractObjectInstance):
    _schema: ClassVar[Optional[Routine]] = None
    _database_class: ClassVar[Type[SplightDatabaseBaseModel]] = RoutineObject

    def to_object(self) -> RoutineObject:
        schema = self._schema

        config = [
            self._convert_to_input_parameter(
                field, getattr(self.config, field.name)
            )
            for field in schema.config
        ]

        input = [
            self._convert_to_input_data_addres(
                field, getattr(self.input, field.name)
            )
            for field in schema.input
        ]

        output = [
            self._convert_to_input_data_addres(
                field, getattr(self.output, field.name)
            )
            for field in schema.output
        ]

        instance = RoutineObject(
            id=self.id,
            name=self.name,
            component_id=self._component_id,
            description=self.description,
            type=self.__class__.__name__,
            status=self.status,
            config=config,
            input=input,
            output=output,
        )
        return instance

    @classmethod
    def from_routine(
        cls,
        routine: Routine,
        component_id: Optional[str] = None,
    ) -> Type["ComponentObjectInstance"]:
        Config = cls._create_config_model(routine.config)
        Input = cls._create_input_model(routine.input)
        Output = cls._create_output_model(routine.output)

        fields = {
            "status": (RoutineStatus, ...),
            "config": (Config, ...),
            "input": (Input, ...),
            "output": (Output, ...),
        }

        fields.update(
            {
                "_schema": (
                    ClassVar[Optional[Routine]],
                    routine,
                ),
                "_component_id": (ClassVar[Optional[str]], component_id),
            }
        )
        model_class = create_model(routine.name, **fields, __base__=cls)
        return model_class

    @classmethod
    def _create_config_model(cls, parameters: List[Parameter]) -> Type:
        fields = {}
        for field in parameters:
            field_type = DB_MODEL_TYPE_MAPPING.get(
                field.type, ComponentObjectInstance
            )
            field_type = List[field_type] if field.multiple else field_type
            field_type = field_type if field.required else Optional[field_type]
            fields.update({field.name: (field_type, ...)})

        return create_model("Config", **fields)

    @classmethod
    def _create_input_model(cls, parameters: List[DataAdress]) -> Type:
        fields = {}
        for field in parameters:
            field_type = (
                List[DLDataAddress] if field.multiple else DLDataAddress
            )
            field_type = field_type if field.required else Optional[field_type]
            fields.update({field.name: (field_type, ...)})
        return create_model("Input", **fields)

    @classmethod
    def _create_output_model(cls, parameters: List[DataAdress]) -> Type:
        fields = {}
        for field in parameters:
            field_type = (
                List[DLDataAddress] if field.multiple else DLDataAddress
            )
            field_type = field_type if field.required else Optional[field_type]
            fields.update({field.name: (field_type, ...)})
        return create_model("Output", **fields)

    @classmethod
    def from_object(
        cls, instance: RoutineObject
    ) -> Type["RoutineObjectInstance"]:
        instance_dict = instance.dict()
        instance_dict["name"] = instance_dict.pop("type")
        return cls.from_routine(
            Routine.parse_obj(instance_dict), instance.component_id
        )

    @classmethod
    def parse_object(cls, instance: RoutineObject) -> "RoutineObjectInstance":
        params_dict = {
            "id": instance.id,
            "name": instance.name,
            "description": instance.description,
            "status": instance.status,
            "config": {
                field.name: get_field_value(field) for field in instance.config
            },
            "input": {
                field.name: get_field_value(field) for field in instance.input
            },
            "output": {
                field.name: get_field_value(field) for field in instance.output
            },
        }
        return cls.parse_obj(params_dict)
