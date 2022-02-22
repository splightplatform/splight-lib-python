from pydantic import BaseModel
from typing import Optional


class Geopoint(BaseModel):
    id: Optional[str]
    latitude: float
    longitude: float
