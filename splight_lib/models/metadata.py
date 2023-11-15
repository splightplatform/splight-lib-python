from typing import Any, Optional

from pydantic import model_validator

from splight_lib.models.base import SplightDatabaseBaseModel
from splight_lib.models.generic import ValueTypeEnum, cast_value


class Metadata(SplightDatabaseBaseModel):
    id: Optional[str] = None
    name: str
    asset: Optional[str] = None
    type: ValueTypeEnum = ValueTypeEnum.NUMBER
    value: Optional[Any] = None

    @model_validator(mode="after")
    def check_value_type(cls, model):
        if model.value is None:
            return model
        model.value = cast_value(model.value, model.type)
        return model
