from datetime import datetime
from typing import Optional

from splight_models.base import SplightBaseModel


class Credential(SplightBaseModel):
    access_id: str
    secret_key: Optional[str] = None
    created_date: Optional[datetime] = None
    last_used: Optional[datetime] = None
    user: Optional[int] = None
    description: Optional[str] = None
