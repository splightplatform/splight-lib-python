from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, EmailStr, Field
from typing_extensions import TypedDict

from splight_lib.constants import DESCRIPTION_MAX_LENGTH
from splight_lib.models.base import SplightDatabaseBaseModel


class AlertStatus(str, Enum):
    ALERT = "alert"
    NO_ALERT = "no_alert"
    NO_DATA = "no_data"
    DISABLED = "disabled"


class AlertOperator(str, Enum):
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "ge"
    LOWER_THAN = "lt"
    LOWER_THAN_OR_EQUAL = "le"
    EQUAL = "eq"


class AlertVariableType(str, Enum):
    STR = "str"
    INT = "int"
    FLOAT = "float"


class VariableDict(TypedDict):
    name: str
    type: str
    value: Union[str, Dict]


class AlertCondition(BaseModel):
    id: Optional[str] = Field(None, max_length=100)
    name: str
    type: AlertVariableType = AlertVariableType.FLOAT
    left_operand: str
    right_operand: str
    variables: List[VariableDict] = []
    operator: AlertOperator = AlertOperator.EQUAL


class Alert(SplightDatabaseBaseModel):
    id: Optional[str] = Field(None, max_length=100)
    name: str
    description: Optional[str] = Field(
        default=None, max_length=DESCRIPTION_MAX_LENGTH
    )
    message: str
    period: float = 1.0
    active: bool = True
    status: AlertStatus = AlertStatus.NO_ALERT
    notification_emails: List[EmailStr] = Field(default_factory=list)
    conditions: List[AlertCondition] = []
