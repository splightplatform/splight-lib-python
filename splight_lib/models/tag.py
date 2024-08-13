from typing import Optional

from splight_lib.models.base import SplightDatabaseBaseModel


class Tag(SplightDatabaseBaseModel):
    id: Optional[str] = None
    name: str
