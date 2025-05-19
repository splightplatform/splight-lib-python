import warnings
from enum import auto

from pydantic import BaseModel
from strenum import PascalCaseStrEnum

warnings.filterwarnings("ignore", category=UserWarning)


class ValueType(PascalCaseStrEnum):
    NUMBER = auto()
    BOOLEAN = auto()
    STRING = auto()


class AttributeType(PascalCaseStrEnum):
    COMPUTED = auto()
    INPUT = auto()
    OUTPUT = auto()


class ResourceSummary(BaseModel):
    id: str | None = None
    name: str
