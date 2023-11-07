from enum import auto
from typing import List, Optional

from pydantic import BaseModel, Field
from strenum import LowercaseStrEnum, UppercaseStrEnum
from typing_extensions import TypedDict

from splight_lib.models.base import SplightDatabaseBaseModel


class FunctionItemType(UppercaseStrEnum):
    EXPRESSION = auto()
    QUERY = auto()


class QueryFilter(TypedDict):
    id: str
    name: str


class GroupUnit(LowercaseStrEnum):
    SECOND = auto()
    MINUTE = auto()
    HOUR = auto()
    DAY = auto()
    MONTH = auto()


class GroupCriteria(LowercaseStrEnum):
    EMPTY = ""
    AVG = auto()
    SUM = auto()
    MIN = auto()
    MAX = auto()
    LAST = auto()


class FunctionItem(BaseModel):
    id: Optional[str] = Field(None, max_length=100)
    ref_id: str
    type: FunctionItemType = FunctionItemType.QUERY
    expression: str = ""
    query_filter_asset: Optional[QueryFilter]
    expression_plain: Optional[str]
    expression_plain: Optional[str]
    query_group_unint: Optional[GroupUnit]
    query_group_function: Optional[GroupCriteria]
    query_sort_field: Optional[str]
    query_sort_direction: Optional[int]
    query_plain: Optional[str]


class Function(SplightDatabaseBaseModel):
    id: Optional[str] = Field(None, max_length=100)
    name: str
    description: Optional[str]

    active: bool = True
    frequency: int = 60
    time_window: int = 5 * 60
    function_items: List[FunctionItem] = []

    target_variable: str
    target_asset: Optional[str] = Field(None, alias="target_asset_id")
    target_attribute: Optional[str] = Field(None, alias="target_attribute_id")
