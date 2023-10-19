from enum import auto
from typing import Optional

from strenum import PascalCaseStrEnum

from splight_lib.models.base import SplightDatabaseBaseModel


class MetadataType(PascalCaseStrEnum):
    NUMBER = auto()
    BOOLEAN = auto()
    STRING = auto()


class Metadata(SplightDatabaseBaseModel):
    id: Optional[str]
    name: Optional[str]
    asset: Optional[str]
    type: MetadataType = MetadataType.NUMBER
    value: Optional[str]
