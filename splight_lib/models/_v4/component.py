import re
import warnings
from abc import ABC, abstractmethod
from enum import auto
from typing import Any, ClassVar, Literal, Optional, Type

from pydantic import (
    BaseModel,
    PrivateAttr,
    create_model,
    field_validator,
    model_validator,
)
from strenum import LowercaseStrEnum, PascalCaseStrEnum

from splight_lib.models._v4.asset import Asset
from splight_lib.models._v4.attribute import Attribute
from splight_lib.models._v4.data_address import DataAddresses as DLDataAddress
from splight_lib.models._v4.datalake_base import SplightDatalakeBaseModel
from splight_lib.models._v4.exceptions import InvalidObjectInstance
from splight_lib.models._v4.file import File
from splight_lib.models._v4.secret import Secret
from splight_lib.models._v4.variable_types import CUSTOM_TYPES, NATIVE_TYPES
from splight_lib.models.database import SplightDatabaseBaseModel

warnings.filterwarnings("ignore", category=RuntimeWarning)


class ComponentStatus(PascalCaseStrEnum):
    RUNNING = auto()
    FAILED = auto()
    SUCCEEDED = auto()


class PrivacyPolicy(LowercaseStrEnum):
    PUBLIC = auto()
    PRIVATE = auto()


class ComponentType(LowercaseStrEnum):
    CONNECTOR = auto()


class RoutineStatus(LowercaseStrEnum):
    RUNNING = auto()
    FAILED = auto()
    PENDING = auto()


class ValueType(PascalCaseStrEnum):
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()
    # The following is just for wrong Routines configurations
    ASSET_ATTRIBUTE = auto()


class Parameter(BaseModel):
    name: str
    description: str = ""
    type: str = "str"
    required: bool = False
    multiple: bool = False
    sensitive: bool = False
    choices: list[Any] | None = None
    depends_on: str | None = None


class InputParameter(Parameter):
    value: Any | None = None


class DataAddress(Parameter):
    choices: None = None
    depends_on: None = None
    required: bool = True
    type: Literal["DataAddress"] = "DataAddress"
    value_type: ValueType = ValueType.NUMBER

    @field_validator("type", mode="before")
    def check_wrong_name(cls, value: str) -> str:
        if value == "DataAdress":
            value = "DataAddress"
        return value


class InputDataAddress(DataAddress):
    value: list[DLDataAddress] | DLDataAddress | None = None

    # NOTE: this is a patch.
    # API returns [] as default for InputDataAddress with multiple set
    # to true.
    @model_validator(mode="after")
    def validate_file(self):
        if self.multiple and self.value is None:
            self.value = []
        return self


class OutputParameter(BaseModel):
    name: str
    description: str | None = None
    type: str
    choices: list[Any] | None = None
    depends_on: str | None = None
    filterable: bool = False


class Output(BaseModel):
    name: str
    fields: list[OutputParameter]


class CustomType(BaseModel):
    name: str
    fields: list[Parameter]

    _reserved_names: ClassVar[list[str]] = ["id", "name", "description"]


class Routine(BaseModel):
    name: str
    max_instances: int | None = None

    config: list[InputParameter] | None = []
    input: list[DataAddress] = []
    output: list[DataAddress] = []

    _reserved_names: ClassVar[list[str]] = ["id", "name", "description"]


class Endpoint(BaseModel):
    name: str | None = None
    port: int | str


class SplightObject(SplightDatabaseBaseModel):
    id: str | None = None
    name: str
    component_id: str | None = None
    description: str | None = None
    type: str

    def save(self):
        if self.component_id is None:
            raise ValueError("component_id cannot be None.")
        super().save()


class ComponentObject(SplightObject):
    data: list[InputParameter] = []


class RoutineEvaluation(SplightDatalakeBaseModel):
    _collection_name = "routine_evaluations"

    routine: str
    status: RoutineStatus
    status_text: str | None


class RoutineObject(SplightObject):
    status: RoutineStatus = RoutineStatus.RUNNING

    config: list[InputParameter] | None = []
    input: list[InputDataAddress] = []
    output: list[InputDataAddress] = []

    def report_status(
        self, status: RoutineStatus, status_text: str | None = None
    ):
        evaluation_status = RoutineEvaluation(
            routine=str(self.id),
            status=status,
            status_text=status_text,
        )
        evaluation_status.save()

        if self.status != status:
            self.status = status
            self._update_status()

    def _update_status(self):
        _ = self._db_client.operate(
            resource_name="routine-status",
            instance={
                "routine": self.id,
                "status": self.status,
            },
        )


class Component(SplightDatabaseBaseModel):
    id: str | None = None
    name: str | None = None
    version: str
    custom_types: list[CustomType] = []
    component_type: ComponentType = ComponentType.CONNECTOR
    input: list[InputParameter] = []
    output: list[Output] = []
    endpoints: list[Endpoint] = []
    routines: list[Routine] = []


DATABASE_TYPES = {
    "Component": Component,
    "Asset": Asset,
    "Attribute": Attribute,
    "File": File,
}

DATALAKE_TYPES = {
    "DataAddress": DLDataAddress,
}

DB_MODEL_TYPE_MAPPING = {
    **NATIVE_TYPES,
    **CUSTOM_TYPES,
    **DATABASE_TYPES,
    **DATALAKE_TYPES,
}


def parse_variable_string(raw_value: str | None) -> Any:
    if raw_value is None:
        return ""
    pattern = re.compile(r"^\$\{\{(\w+)\.(\w+)\}\}$")
    match = pattern.search(raw_value)
    if not match:
        return raw_value
    _, secret_name = match.groups()
    # TODO: handle errors (not found or not allowed)
    secret = Secret.decrypt(name=secret_name)
    return secret.value


def get_field_value(field: InputParameter | list[InputParameter]):
    multiple = field.multiple

    value = field.value
    if value is None:
        return [] if multiple else None

    if field.type in NATIVE_TYPES:
        value = (
            field.value
            if not isinstance(field.value, str)
            else parse_variable_string(field.value)
        )
    elif field.type in CUSTOM_TYPES:
        value = CUSTOM_TYPES.get(field.type).from_string(field.value)
    elif field.type in DATABASE_TYPES:
        model_class = DATABASE_TYPES[field.type]
        value = (
            model_class.retrieve(field.value)
            if not multiple
            else [model_class.retrieve(item) for item in field.value]
        )
    elif field.type in DATALAKE_TYPES:
        model_class = DATALAKE_TYPES[field.type]
        value = (
            [model.model_copy() for model in field.value]
            if multiple
            else [field.value.model_copy()]
        )
        for item in value:
            item.type = field.value_type

        value = [model_class.model_validate(item) for item in value]
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
    id: str | None = None
    name: str = ""
    description: str | None = None

    _default_attrs: list[str] = PrivateAttr(
        ["id", "name", "component_id", "description"]
    )
    _schema: ClassVar[BaseModel | None] = None
    _database_class: ClassVar[Type[SplightDatabaseBaseModel] | None] = None
    _component_id: ClassVar[str | None] = None

    def save(self):
        component_obj = self.to_object()
        component_obj.save()
        if not self.id:
            self.id = component_obj.id

    def delete(self):
        component_obj = self.to_object()
        component_obj.delete()

    @classmethod
    def list(cls, **params: dict) -> list["AbstractObjectInstance"]:
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
        if field.type not in (NATIVE_TYPES | CUSTOM_TYPES):
            value = (
                [item.id for item in field_value]
                if field.multiple
                else field_value.id
            )
        parameter = field.model_dump()
        parameter.update({"value": value})
        return InputParameter.model_validate(parameter)

    @staticmethod
    def _convert_to_input_data_addres(
        field: DataAddress, field_value: Any
    ) -> InputDataAddress:
        if field.multiple:
            value = [
                {
                    "asset": item.asset,
                    "attribute": item.attribute,
                }
                for item in field_value
            ]
        else:
            value = (
                None
                if field_value is None
                else {
                    "asset": field_value.asset,
                    "attribute": field_value.attribute,
                }
            )
        parameter = field.model_dump()
        parameter.update({"value": value})
        return InputDataAddress.model_validate(parameter)

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
    _schema: ClassVar[CustomType | None] = None
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
        component_id: str | None = None,
    ) -> Type["ComponentObjectInstance"]:
        fields = {}

        for field in custom_type.fields:
            field_type = DB_MODEL_TYPE_MAPPING.get(field.type, cls)
            field_type = list[field_type] if field.multiple else field_type
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
        instance_dict = instance.model_dump()
        instance_dict["fields"] = instance_dict.pop("data")
        instance_dict["name"] = instance_dict.pop("type")
        return cls.from_custom_type(
            CustomType.model_validate(instance_dict), instance.component_id
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
        return cls.model_validate(params_dict)

    @classmethod
    def from_component(
        cls,
        component: Component,
    ) -> dict[str, "ComponentObjectInstance"]:
        return {
            ct.name: cls.from_custom_type(ct, component.id)
            for ct in component.custom_types
        }


class RoutineObjectInstance(AbstractObjectInstance):
    _schema: ClassVar[Routine | None] = None
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
        component_id: str | None = None,
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
    def _create_config_model(cls, parameters: list[Parameter]) -> Type:
        fields = {}
        for field in parameters:
            field_type = DB_MODEL_TYPE_MAPPING.get(
                field.type, ComponentObjectInstance
            )
            field_type = list[field_type] if field.multiple else field_type
            field_type = field_type if field.required else Optional[field_type]
            field_value = ... if field.required else None
            fields.update({field.name: (field_type, field_value)})

        return create_model("Config", **fields)

    @classmethod
    def _create_input_model(cls, parameters: list[DataAddress]) -> Type:
        fields = {}
        for field in parameters:
            field_type = (
                list[DLDataAddress] if field.multiple else DLDataAddress
            )
            field_type = field_type if field.required else Optional[field_type]
            field_value = ... if field.required else None
            fields.update({field.name: (field_type, field_value)})
        return create_model("Input", **fields)

    @classmethod
    def _create_output_model(cls, parameters: list[DataAddress]) -> Type:
        fields = {}
        for field in parameters:
            field_type = (
                list[DLDataAddress] if field.multiple else DLDataAddress
            )
            field_type = field_type if field.required else Optional[field_type]
            field_value = ... if field.required else None
            fields.update({field.name: (field_type, field_value)})
        return create_model("Output", **fields)

    @classmethod
    def from_object(
        cls, instance: RoutineObject
    ) -> Type["RoutineObjectInstance"]:
        instance_dict = instance.model_dump()
        instance_dict["name"] = instance_dict.pop("type")
        return cls.from_routine(
            Routine.model_validate(instance_dict), instance.component_id
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
        return cls.model_validate(params_dict)

    def report_status(
        self, status: RoutineStatus, status_text: str | None = None
    ):
        routine_object = self.to_object()
        routine_object.report_status(status=status, status_text=status_text)
