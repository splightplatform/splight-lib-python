import json
from collections import namedtuple
from typing import Annotated, Type

from pydantic import AnyUrl, BaseModel, Field, ValidationInfo, field_validator

from splight_lib.component.exceptions import (
    DuplicatedValuesError,
    ParameterDependencyError,
)
from splight_lib.models import (
    Component,
    ComponentObjectInstance,
    ComponentType,
    CustomType,
    Endpoint,
    InputParameter,
    Output,
    PrivacyPolicy,
    Routine,
    SplightDatalakeBaseModel,
    get_field_value,
)
from splight_lib.utils.custom_model import create_custom_model

VALID_PARAMETER_VALUES = {
    "int": int,
    "bool": bool,
    "str": str,
    "float": float,
    "crontab": str,
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


def check_unique_values(values: list[str]):
    """Checks if there are repeated values in a list of strings.

    Raises
    ------
    DuplicatedValuesError thrown when there is at least two repeated values
    """
    if len(values) != len(set(values)):
        raise DuplicatedValuesError("The list contains duplicated values")


def check_parameter_dependency(parameters: list[InputParameter]):
    """Checks dependency between parameters.

    Raises
    ------
    ParameterDependencyError thrown for an error in the dependency.
    """
    parameter_map: dict[str, InputParameter] = {p.name: p for p in parameters}
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
    name: Annotated[str, Field(pattern=r"^[a-zA-Z0-9\s]+$")]
    version: Annotated[str, Field(pattern=r"^(\d+\.)?(\d+\.)?(\*|\d+)$")]
    splight_lib_version: Annotated[
        str | None,
        Field(pattern=r"^(\d+)\.(\d+)\.(\d+)(?:\.?(dev|rc)(\d+))?$"),
    ] = None
    splight_cli_version: Annotated[
        str | None,
        Field(pattern=r"^(\d+)\.(\d+)\.(\d+)(?:\.?(dev|rc)(\d+))?$"),
    ] = None
    description: str | None = None
    privacy_policy: PrivacyPolicy = PrivacyPolicy.PUBLIC
    tags: set[str] = set()
    component_type: ComponentType = ComponentType.CONNECTOR
    custom_types: list[CustomType] = []
    input: list[InputParameter] = []
    output: list[Output] = []
    routines: list[Routine] = []
    endpoints: list[Endpoint] = []

    @field_validator("custom_types", mode="after")
    def validate_custom_types(
        cls, custom_types: list[CustomType], info: ValidationInfo
    ) -> list[CustomType]:
        try:
            check_unique_values([item.name for item in custom_types])
        except DuplicatedValuesError as exc:
            raise ValueError("Repeated Custom Types in spec") from exc

        valid_types: list[str] = VALID_PARAMETER_VALUES.keys()
        custom_type_names: list[str] = []

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

    @field_validator("input", mode="after")
    def validate_parameters(
        cls, input: list[InputParameter], info: ValidationInfo
    ) -> list[InputParameter]:
        values = info.data
        try:
            check_unique_values([item.name for item in input])
        except DuplicatedValuesError as exc:
            raise ValueError("Repeated Input parameters in spec") from exc

        custom_type_names: list[str] = [c.name for c in values["custom_types"]]
        valid_types_names: list[str] = (
            list(VALID_PARAMETER_VALUES.keys()) + custom_type_names
        )

        for parameter in input:
            if parameter.type not in valid_types_names:
                raise ValueError(f"Input type {parameter.type} not defined")

        try:
            check_parameter_dependency(input)
        except ParameterDependencyError as exc:
            raise ValueError("Invalid parameter dependecy") from exc
        return input

    @field_validator("output", mode="after")
    def validate_output(cls, output: list[Output]) -> list[Output]:
        try:
            check_unique_values([item.name for item in output])
        except DuplicatedValuesError as exc:
            raise ValueError("Repeated output parameters") from exc
        return output

    @classmethod
    def from_file(cls, file_path: str) -> "Spec":
        with open(file_path, "r") as fid:
            data = json.load(fid)
        return cls.model_validate(data)

    def get_input_model(self) -> Type[BaseModel]:
        """Creates a BaseModel class that represents the component's input.

        Returns
        -------
        Type[BaseModel] the class object for the input.
        """
        custom_type_dict = {
            ct.name: ComponentObjectInstance.from_custom_type(
                ct, component_id=None
            )
            for ct in self.custom_types
        }
        model = create_custom_model(
            model_name="Input",
            parameters=self.input,
            custom_types=custom_type_dict,
            config_dict={"use_enum_values": True},
        )
        return model

    def component_input(self, component_id: str) -> BaseModel:
        """Creates the input for the component given the id. The parameters
        values are retrieved from the database.

        Parameters
        ----------
        component_id: str
            The components

        Returns
        -------
        BaseModel: The component's input.
        """
        input_model = self.get_input_model()
        component = Component.retrieve(component_id)
        values = {
            param.name: get_field_value(param) for param in component.input
        }
        return input_model.model_validate(values)

    def get_output_models(self, component_id: str) -> BaseModel:
        """Creates a BaseModel that represents the component's output. Each
        of the defined outputs in the spec are attributes which values
        are class objects.

        Parameters
        ----------
        component_id: str
            The component's id.

        Returns
        -------
        BaseModel the output model.
        """
        fields = {}
        class_vars = [
            {"name": "_collection_name", "type": str, "value": component_id}
        ]
        for output in self.output:
            model_class = create_custom_model(
                model_name=output.name,
                parameters=output.fields,
                class_vars=class_vars,
                base_class=SplightDatalakeBaseModel,
            )
            fields.update({output.name: model_class})

        output_model_class = namedtuple(
            "Output", [key for key in fields.keys()]
        )
        return output_model_class(**fields)
