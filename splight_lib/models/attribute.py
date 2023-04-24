from typing import Optional

from splight_lib.models.base import SplightDatabaseBaseModel


class Attribute(SplightDatabaseBaseModel):
    id: Optional[str]
    name: str
