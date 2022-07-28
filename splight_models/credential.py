from typing import List, Optional
from .base import SplightBaseModel
from datetime import datetime


class Credential(SplightBaseModel):
    secret_key: Optional[str]
    access_id: str
    user: str
    created_date: datetime
    last_used: datetime
