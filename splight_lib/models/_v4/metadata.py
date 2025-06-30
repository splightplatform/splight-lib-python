from typing import Any

from pydantic import model_validator

from splight_lib.models._v4.base import ValueType
from splight_lib.models._v4.exceptions import InvalidOperation
from splight_lib.models._v4.generic import cast_value, is_empty_str_and_num
from splight_lib.models.database import SplightDatabaseBaseModel


class Metadata(SplightDatabaseBaseModel):
    id: str | None = None
    asset: str | None = None
    name: str
    description: str | None = None
    type: ValueType
    unit: str | None = None
    value: Any | None = None

    def save(self) -> None:
        raise InvalidOperation("save")

    def delete(self) -> None:
        raise InvalidOperation("delete")

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
