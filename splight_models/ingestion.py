from .base import SplightBaseModel
from typing import Optional

class Ingestion(SplightBaseModel):
  name: str
  description: Optional[str]
  id: Optional[str]

