from datetime import datetime
from pydantic import BaseModel
from typing import Dict, Optional


class Variable(BaseModel):
    args: Dict
    path: Optional[str] = None
    asset_id: Optional[str] = None
    attribute_id: Optional[str] = None
    timestamp: Optional[datetime] = None
