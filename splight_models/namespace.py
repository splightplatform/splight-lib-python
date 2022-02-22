from pydantic import BaseModel
from typing import Optional, Dict


class Namespace(BaseModel):
    id: Optional[str]
    environment: Dict = {}
