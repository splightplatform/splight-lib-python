from splight_models.base import SplightBaseModel
from datetime import datetime
from typing import Dict, Optional, Type
from pydantic import Field, BaseModel
from datetime import datetime, timezone

class RTEvent(SplightBaseModel):
    type: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
    display_text: Optional[str]
    data: Dict