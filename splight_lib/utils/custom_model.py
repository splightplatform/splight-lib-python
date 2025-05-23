from enum import Enum
from typing import Any, ClassVar, Optional, Type

from pydantic import BaseModel, create_model
from typing_extensions import TypedDict

from splight_lib.models import DB_MODEL_TYPE_MAPPING, Parameter


class ClassVarDict(TypedDict):
    name: str
    type: str
    value: Any


def create_custom_model(
    model_name: str,
    parameters: list[Parameter],
    custom_types: dict | None = None,
    base_class: Type[BaseModel] | None = None,
    config_dict: dict[str, Any] | None = None,
    class_vars: list[ClassVarDict] | None = None,
) -> Type[BaseModel]:
    """
    Function to create custom pydantic model specific for components.

    Parameters
    ----------
    model_name: str
        The name for the model
    parameters: List[Parameter]
        The list of Parameter used for the model attributes.
    custom_types: Optional[Dict]
        Dict with the custom types models.
    config_class: Optional[Type]
        The config class for the new model.

    Returns
    -------
    The model constructor.
    """
    custom_type_dict = custom_types if custom_types else {}
    fields = {}
    for param in parameters:
        name = param.name
        choices = getattr(param, "choices", None)
        multiple = getattr(param, "multiple", False)
        required = getattr(param, "required", True)

        single_param_type = DB_MODEL_TYPE_MAPPING.get(param.type, None)
        if not single_param_type:
            single_param_type = custom_type_dict.get(param.type)

        if choices:
            valid_choices = Enum(
                f"{name.title()}Choices",
                {item.upper(): item for item in choices},
            )
            single_param_type = valid_choices

        param_type = list[single_param_type] if multiple else single_param_type
        param_type = param_type if required else Optional[param_type]

        value = Ellipsis if required else None
        fields.update({name: (param_type, value)})

    if class_vars:
        fields.update(
            {
                var["name"]: (ClassVar[var["type"]], var["value"])
                for var in class_vars
            }
        )
    return create_model(
        model_name, **fields, __base__=base_class, __config__=config_dict
    )
