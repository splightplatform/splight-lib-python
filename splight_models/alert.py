import builtins
import operator
from typing import List, Optional, Union
from uuid import UUID

from pydantic import EmailStr, Field, validator

from splight_models.base import SplightBaseModel
from splight_models.constants import (
    AlertOperator,
    AlertStatus,
    AlertVariableType,
)

from .query import Query


class InvalidValueType(Exception):
    def __init__(self, value_type: str, target_type: str):
        self._msg = (
            f"Invalid value type, expected type {target_type}. "
            f"Got {value_type}"
        )

    def __str__(self) -> str:
        return self._msg


class AlertCondition(SplightBaseModel):
    id: Optional[str] = Field(None, max_length=100)
    # TODO: not use this models in Splight API repository
    query: Union[str, Query]
    operator: AlertOperator = AlertOperator.EQUAL
    threshold: str
    type: AlertVariableType = AlertVariableType.FLOAT
    namespace: str = Field("default", alias="namespace_id")
    deleted: bool = False

    def is_satisfied(self, value: Union[float, int, str]) -> bool:
        """Check if the condition is satisfied.

        Parameters
        ----------
        value: Union[float, int, str]
            The value to be compared againts the threshold using operator

        Returns
        -------
        bool: True is the condition is satisfied, False otherwise.

        Raises
        ------
        InvalidValueType thrown when the value's type is different for the
        condition type
        """
        type_builder = getattr(builtins, self.type)
        threshold = type_builder(self.threshold)
        if not isinstance(value, type_builder):
            raise InvalidValueType(str(type(value)), self.type)
        return getattr(operator, self.operator)(value, threshold)


class Alert(SplightBaseModel):
    id: Optional[str] = Field(None, max_length=100)
    name: str
    descriptIon: Optional[str] = None
    message: str
    period: float = 1.0
    active: bool = True
    status: AlertStatus = AlertStatus.NO_ALERT
    notification_emails: List[EmailStr] = Field(default_factory=list)
    namespace: str = Field("default", alias="namespace_id")
    deleted: bool = False
    condition: Optional[AlertCondition] = None

    @validator("id", pre=True)
    def convert_to_str(cls, value: Union[str, UUID]):
        return str(value)

    @validator("namespace", pre=True)
    def validate_namespace(cls, value: Optional[str]):
        return value if value else "default"

    def check_alert(self, value: Union[float, int, str]) -> bool:
        return self.condition.is_satisfied(value)
