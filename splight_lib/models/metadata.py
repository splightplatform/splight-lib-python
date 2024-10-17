from typing import Any

from pydantic import model_validator

from splight_lib.models.database_base import SplightDatabaseBaseModel
from splight_lib.models.generic import ValueTypeEnum, cast_value


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
            if model.value is None or model.value == ""
            else cast_value(model.value, model.type)
        )
        return model
