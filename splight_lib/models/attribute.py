from enum import auto
from typing import Optional

from strenum import PascalCaseStrEnum

from splight_lib.models.base import SplightDatabaseBaseModel


class AttributeType(PascalCaseStrEnum):
    NUMBER = auto()
    BOOLEAN = auto()
    STRING = auto()


class Attribute(SplightDatabaseBaseModel):
    id: Optional[str]
    name: str
    asset: Optional[str]
    type: AttributeType = AttributeType.NUMBER
