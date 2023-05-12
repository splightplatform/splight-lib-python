# from enum import auto
from typing import Dict, List, Optional, Set

# from cli.constants import VALID_DEPENDS_ON, VALID_PARAMETER_VALUES
from pydantic import AnyUrl, BaseModel, Field, ValidationError, validator

from splight_lib.models.component import ComponentType  # Parameter,
from splight_lib.models.component import (
    Command,
    CustomType,
    Endpoint,
    InputParameter,
    Output,
    PrivacyPolicy,
)

# from strenum import LowercaseStrEnum


# from splight_models import CustomType as ModelCustomType
# from splight_models import Deployment as ModelDeployment
# from splight_models import CommandParameter as ModelCommandParameter
# from splight_models import Endpoint as ModelEndpoint
# from splight_models import InputParameter as ModelInputParameter
# from splight_models import Output as ModelOutput
# from splight_models import OutputParameter as ModelOutputParameter
# from splight_models import Parameter as ModelParameter

# from splight_models.constants import ComponentType


# class ChoiceMixin:
#     @validator("choices", check_fields=False)
#     def validate_choices(cls, v, values):
#         if "type" not in values:
#             return v
#
#         type_ = values["type"]
#
#         if type not in ["str", "int", "float"]:
#             raise ValueError(
#                 "Choices can only be used with string, int or float types"
#             )
#
#         # choises type match type field
#         try:
#             class_type = VALID_PARAMETER_VALUES[type_]
#             [isinstance(c, class_type) for c in v]
#         except Exception as exc:
#             raise ValueError(
#                 f"choices must be list of type {str(class_type)}"
#             ) from exc
#
#         return v
#
#
# class Parameter(ModelInputParameter, ChoiceMixin):
#     @validator("value", check_fields=False)
#     def validate_value(cls, v, values, field):
#         if not set(values.keys()).issuperset(
#             {"type", "required", "multiple", "choices"}
#         ):
#             return v
#
#         type_ = values["type"]
#
#         # allow custom type
#         if type_ not in VALID_PARAMETER_VALUES:
#             return v
#
#         # UUIDs and Date must be None
#         if VALID_PARAMETER_VALUES[type_] is None:
#             return v
#
#         # if values["required"] and v is None:
#         #     raise ValueError("value must be set")
#
#         # if values["multiple"]:
#         #     if not isinstance(v, list):
#         #         raise ValueError("value must be a list")
#
#         # Make all parameter values a list
#         list_v = v if isinstance(v, list) else [v]
#
#         # value type match type field
#         try:
#             class_type = VALID_PARAMETER_VALUES[type_]
#             [isinstance(v_, class_type) for v_ in list_v]
#         except Exception as exc:
#             raise ValueError(
#                 f"value must be of type {str(class_type)}"
#             ) from exc
#
#         if values["choices"] is not None and not all(
#             [v_ in values["choices"] for v_ in list_v]
#         ):
#             raise ValueError(f"value must be one of {values['choices']}")
#
#         return v
#
#
# class OutputParameter(ModelOutputParameter, ChoiceMixin):
#     @validator("type", check_fields=False)
#     def validate_type(cls, type):
#         if type not in VALID_PARAMETER_VALUES:
#             raise ValueError(
#                 f"invalid output type {type}, can not be custom type"
#             )
#         return type
#
#
# class CommandParameter(ModelCommandParameter, ChoiceMixin):
#     @validator("type", check_fields=False)
#     def validate_type(cls, type):
#         if type not in VALID_PARAMETER_VALUES:
#             raise ValueError(
#                 f"invalid output type {type}, can not be custom type"
#             )
#         return type
#
#
# class FieldMixin:
#     @validator("fields")
#     def validate_fields(cls, fields):
#         if len(fields) == 0:
#             raise ValueError("fields must not be empty")
#
#         _check_unique_names(fields, "fields")
#         _check_parameter_depends_on(fields)
#
#         return fields
#
#
# class CustomType(ModelCustomType, FieldMixin):
#     fields: List[ModelParameter]
#
#
# class Output(ModelOutput, FieldMixin):
#     fields: List[OutputParameter]
#
#
# class Endpoint(ModelEndpoint):
#     name: str
#     port: int

VALID_PARAMETER_VALUES = {
    "int": int,
    "bool": bool,
    "str": str,
    "float": float,
    "url": AnyUrl,
    "datetime": None,
    "File": None,  # UUID
    "Asset": None,  # UUID,
    "Attribute": None,  # UUID,
    "Component": None,  # UUID,
}


VALID_DEPENDS_ON = [
    ("Attribute", "Asset"),
]


class DuplicatedValuesError(Exception):
    pass


class ParameterDependencyError(Exception):
    pass


def check_unique_values(values: List[str]):
    if len(values) != len(set(values)):
        raise DuplicatedValuesError("The list contains duplicated values")


def check_parameter_dependency(parameters: List[InputParameter]):
    parameter_map: Dict[str, InputParameter] = {p.name: p for p in parameters}
    for parameter in parameters:
        if not parameter.depends_on:
            continue

        depend_parameter = parameter_map[parameter.depends_on]
        if (parameter.type, depend_parameter.type) not in VALID_DEPENDS_ON:
            raise ParameterDependencyError(
                f"Incompatible dependency: type {parameter.type} can not"
                f"depend on type {depend_parameter.type}"
            )


class Spec(BaseModel):
    name: str = Field(regex=r"^[a-zA-Z0-9\s]+$")
    version: str = Field(regex=r"^(\d+\.)?(\d+\.)?(\*|\d+)$")
    splight_cli_version: str = Field(regex=r"^(\d+\.)?(\d+\.)?(\*|\d+)$")
    description: Optional[str]
    privacy_policy: PrivacyPolicy = PrivacyPolicy.PUBLIC
    tags: Set[str] = set()
    component_type: ComponentType = ComponentType.CONNECTOR
    custom_types: List[CustomType] = []
    input: List[InputParameter] = []
    output: List[Output] = []
    commands: List[Command] = []
    endpoints: List[Endpoint] = []

    @validator("custom_types")
    def validate_custom_types(
        cls, custom_types: List[CustomType]
    ) -> List[CustomType]:
        try:
            check_unique_values([item.name for item in custom_types])
        except DuplicatedValuesError as exc:
            raise ValueError("Repeated Custom Types in spec") from exc

        valid_types: List[str] = VALID_PARAMETER_VALUES.keys()
        custom_type_names: List[str] = []

        for custom_type in custom_types:
            for field in custom_type.fields:
                name = field.name
                if (
                    field.type not in valid_types
                    and field.type not in custom_type_names
                ):
                    raise ValueError(f"CustomType {field.type} not defined")
                if name in CustomType._reserved_names:
                    raise ValueError(
                        f"Field '{name}' in CustomType {custom_type.name} "
                        f"is not a valid field. Reserved names "
                        f"are: {CustomType._reserved_names}"
                    )
            custom_type_names.append(custom_type.name)

        return custom_types

    @validator("input")
    def validate_parameters(
        cls, input: List[InputParameter], values: Dict,
    ) -> List[InputParameter]:
        try:
            check_unique_values([item.name for item in input])
        except DuplicatedValuesError as exc:
            raise ValueError("Repeated Input parameters in spec") from exc

        custom_type_names: List[str] = [c.name for c in values["custom_types"]]
        valid_types_names: List[str] = (
            list(VALID_PARAMETER_VALUES.keys()) + custom_type_names
        )

        for parameter in input:
            if parameter.type not in valid_types_names:
                raise ValueError(f"input type {parameter.type} not defined")

        try:
            check_parameter_dependency(input)
        except ParameterDependencyError as exc:
            raise ValueError("Invalid parameter dependecy") from exc
        return input

    @validator("output")
    def validate_output(cls, output: List[Output]) -> List[Output]:
        try:
            check_unique_values([item.name for item in output])
        except DuplicatedValuesError as exc:
            raise ValueError("Repeated output parameters") from exc
        return output

    @classmethod
    def from_file(cls, file_path: str) -> "Spec":
        return cls.parse_file(file_path)
