from enum import Enum
from typing import Dict, List, Optional, Type

from pydantic import BaseModel, create_model
from splight_lib.models.component import DB_MODEL_TYPE_MAPPING, Parameter


def create_custom_model(
    model_name: str,
    parameters: List[Parameter],
    custom_types: Optional[Dict] = None,
    config_class: Optional[Type] = None,
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

        param_type = List[single_param_type] if multiple else single_param_type
        param_type = param_type if required else Optional[param_type]

        value = Ellipsis if required else None
        fields.update({name: (param_type, value)})
    return create_model(model_name, **fields, __config__=config_class)
