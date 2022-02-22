from pydantic import BaseModel
from typing import List, Optional


class DigitalOfferComponent(BaseModel):
    id: Optional[str]
    name: str


class DigitalOffer(BaseModel):
    id: Optional[str]
    name: str
    component_ids: List[str]


class RunningDigitalOffer(BaseModel):
    id: Optional[str]
    tag_ids: List[str]
    digital_offer_id: str
