from pydantic import BaseModel

from splight_lib.models._v4.base import ResourceSummary, ValueType
from splight_lib.models.database import SplightDatabaseBaseModel


class SolutionOutput(BaseModel):
    id: str | None = None
    name: str
    type: ValueType
    unit: str | None = None


class SolutionConfiguration(BaseModel):
    id: str | None = None
    name: str
    type: ValueType
    unit: str | None = None
    value: str | float | bool | None = None


class Solution(SplightDatabaseBaseModel):
    id: str | None = None
    name: str
    description: str | None = None
    type: str
    tags: list[str] = []
    asset: ResourceSummary
    outputs: list[SolutionOutput] = []
    configurations: list[SolutionConfiguration] = []
