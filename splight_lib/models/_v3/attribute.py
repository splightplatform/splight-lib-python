from enum import auto

from strenum import PascalCaseStrEnum

from splight_lib.models.database import SplightDatabaseBaseModel


class AttributeType(PascalCaseStrEnum):
    NUMBER = auto()
    BOOLEAN = auto()
    STRING = auto()


class Attribute(SplightDatabaseBaseModel):
    id: str | None = None
    name: str
    asset: str | None = None
    type: AttributeType = AttributeType.NUMBER
    unit: str | None = None
