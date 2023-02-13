from typing import Optional

from pydantic import Field
from splight_models.base import SplightBaseModel
from splight_models.constants import SeverityType, AlertOperator


class Alert(SplightBaseModel):
    id: Optional[str] = Field(None, max_length=100)
    query_id: str = Field(..., max_length=100)
    value: str
    message: str
    name: str
    description: Optional[str] = None
    severity: SeverityType
    operator: AlertOperator
    period: float = 1.0
