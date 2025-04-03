from typing import Any

from pydantic import model_validator

from splight_lib.models._v3.generic import (
    ValueTypeEnum,
    cast_value,
    is_empty_str_and_num,
)
from splight_lib.models.database import SplightDatabaseBaseModel


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

    def set(self, value: float | str | bool) -> None:
        self._db_client.operate(
            "set-asset-metadata",
            instance={
                "metadata": self.id,
                "value": str(value),
            },
        )
