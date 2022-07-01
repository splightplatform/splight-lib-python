from pydantic import Field
from .base import SplightBaseModel
from typing import Optional


class Organization(SplightBaseModel):
    id: Optional[str]
    auth0_id: str
    display_name: str
    active: bool = False