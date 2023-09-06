from typing import Optional
from enum import auto

from strenum import PascalCaseStrEnum

from splight_lib.models.base import SplightDatabaseBaseModel


class AttributeType(PascalCaseStrEnum):
    NUMBER = auto()
    BOOLEAN = auto()
    STRING = auto()


class Attribute(SplightDatabaseBaseModel):
    id: Optional[str]
    name: str
    asset: str
    type: AttributeType = AttributeType.NUMBER

    def save(self):
        raise NotImplementedError("Attribute object can't be saved")
