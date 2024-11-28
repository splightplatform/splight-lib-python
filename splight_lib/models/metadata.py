from typing import Any

from pydantic import model_validator

from splight_lib.models.database_base import SplightDatabaseBaseModel
from splight_lib.models.generic import (
    ValueTypeEnum,
    cast_value,
    is_empty_str_and_num,
)


class Metadata(SplightDatabaseBaseModel):
    id: str | None = None
    name: str
    asset: str | None = None
    type: ValueTypeEnum = ValueTypeEnum.NUMBER
    value: Any | None = None
    unit: str | None = None

    @model_validator(mode="after")
    def check_value_type(cls, model):
        model.value = (
            None
            if model.value is None
            or is_empty_str_and_num(model.value, model.type)
            else cast_value(model.value, model.type)
        )
        return model
