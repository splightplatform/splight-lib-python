from datetime import datetime
from enum import auto
from typing import List, Optional, Union

from pydantic import BaseModel, ValidationError, validator
from splight_lib.models.asset import Asset
from splight_lib.models.attribute import Attribute
from splight_lib.models.base import SplightDatabaseBaseModel
from strenum import LowercaseStrEnum, PascalCaseStrEnum


class SetPointType(PascalCaseStrEnum):
    Number = auto()
    String = auto()
    Boolean = auto()

    def __str__(self):
        return self.value


class SetPointResponseStatus(LowercaseStrEnum):
    SUCCESS = auto()
    ERROR = auto()
    IGNORE = auto()

    def __str__(self):
        return self.value


class SetPointResponse(BaseModel):
    id: Optional[str]
    component: str
    status: SetPointResponseStatus
    created_at: Optional[datetime] = None


class SetPoint(SplightDatabaseBaseModel):
    id: Optional[str]
    asset: Asset
    attribute: Attribute
    type: SetPointType
    value: Union[str, bool, float]
    responses: List[SetPointResponse] = []

    @validator("value")
    def cast_value(cls, v, values, **kwargs):
        if "type" not in values:
            raise ValueError("type is required")

        mapping_functions = {
            SetPointType.Number: float,
            SetPointType.Boolean: bool,
            SetPointType.String: str,
        }
        parse_function = mapping_functions.get(values["type"])
        try:
            parsed_value = parse_function(v)
        except ValueError as exc:
            raise ValidationError(f"value must be a {str(type)}") from exc
        return parsed_value

    def save(self):
        new_value = self.asset.set_attribute(
            attribute=self.attribute, value=self.value, value_type=self.type
        )
        if not self.id:
            self.id = new_value["id"]
