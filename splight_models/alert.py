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
    SeverityType,
)


class Alert(SplightBaseModel):
    id: Optional[str] = Field(None, max_length=100)
    query_id: str = Field(..., max_length=100)
    query: Optional[Query] = None
    type: AlertVariableType = AlertVariableType.FLOAT
    threshold: str
    message: str
    name: str
    description: Optional[str] = None
    severity: SeverityType = SeverityType.info
    operator: AlertOperator = AlertOperator.EQUAL
    period: float = 1.0
    namespace: str = Field("default", alias="namespace_id")
    deleted: bool = False

    @validator("id", pre=True)
    def convert_to_str(cls, value: Union[str, UUID]):
        return str(value)

    def is_satisfied(self, value: Union[float, int, str]) -> bool:
        rule_value = getattr(builtins, self.type)(self.threshold)
        value = getattr(builtins, self.type)(value)
        return getattr(operator, self.operator)(value, rule_value)
