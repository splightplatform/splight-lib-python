import builtins
import operator
from uuid import UUID
from typing import Optional, Union

from pydantic import Field, validator

from splight_models.base import SplightBaseModel
from .query import Query
from splight_models.constants import (
    AlertOperator,
    AlertVariableType,
    # SeverityType,
)


class AlertCondition(SplightBaseModel):
    id: Optional[str] = Field(None, max_length=100)
    query: Query
    operator: AlertOperator = AlertOperator.EQUAL
    threshold: str
    type: AlertVariableType = AlertVariableType.FLOAT
    namespace: str = Field("default", alias="namespace_id")
    deleted: bool = False

    @validator("id", pre=True)
    def convert_to_str(cls, value: Union[str, UUID]):
        return str(value)


class Alert(SplightBaseModel):
    id: Optional[str] = Field(None, max_length=100)
    message: str
    name: str
    description: Optional[str] = None
    period: float = 1.0
    namespace: str = Field("default", alias="namespace_id")
    deleted: bool = False
    condition: AlertCondition

    @validator("id", pre=True)
    def convert_to_str(cls, value: Union[str, UUID]):
        return str(value)

    def is_satisfied(self, value: Union[float, int, str]) -> bool:
        __import__('ipdb').set_trace()
        rule_value = getattr(builtins, self.type)(self.threshold)
        value = getattr(builtins, self.type)(value)
        return getattr(operator, self.operator)(value, rule_value)
