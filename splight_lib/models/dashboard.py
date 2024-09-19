from enum import auto
from typing import Annotated, Any

from pydantic import BaseModel, Field
from strenum import UppercaseStrEnum

from splight_lib.constants import DESCRIPTION_MAX_LENGTH
from splight_lib.models.database_base import (
    ResourceSummary,
    SplightDatabaseBaseModel,
)


class ChartItemType(UppercaseStrEnum):
    QUERY = auto()
    EXPRESSION = auto()


class Threshold(BaseModel):
    color: str | None = None
    display_text: str | None = None
    value: float | None = None


class ValueMapping(BaseModel):
    display_text: str | None = None
    order: int = 0


class ExactMatchValueMapping(ValueMapping):
    match_value: str | None = None


class RangeValueMapping(ValueMapping):
    range_start: float | None = None
    range_end: float | None = None


class RegexMatchValueMapping(ValueMapping):
    regular_expression: str | None = None


class Filter(SplightDatabaseBaseModel):
    id: str | None = None
    chart_item: str
    operator: str | None = None
    key: str | None = None
    value: str | None = None
    label: str | None = None


class AdvancedFilter(SplightDatabaseBaseModel):
    id: str | None = None
    chart_item: str
    operator: str | None = None
    key: str | None = None
    field: str | None = None
    value: str | None = None


class ChartItem(BaseModel):
    id: str | None = None
    type: ChartItemType = ChartItemType.QUERY
    ref_id: str
    label: str
    order: int | None = None
    color: str | None = None
    hidden: bool = False
    query_filter_asset: ResourceSummary | None = None
    query_filter_attribute: ResourceSummary | None = None
    query_group_unit: str | None = None
    query_group_function: str | None = None
    query_sort_field: str | None = None
    query_sort_direction: int | None = -1
    query_limit: int = 10000
    query_plain: str = ""
    position_x: int | None = None
    position_y: int | None = None
    expression: str | None = None
    expression_plain: str | None = None


class Chart(SplightDatabaseBaseModel):
    id: str | None = None
    name: str
    description: Annotated[
        str | None, Field(max_length=DESCRIPTION_MAX_LENGTH)
    ] = None
    items: list[ChartItem] | None = None
    tab: str
    position_x: int | None = None
    position_y: int | None = None
    height: int | None = 28
    width: int | None = 80
    min_height: int | None = 14
    min_width: int | None = 14
    type: str | None = None
    timestamp_gte: str | None = None
    timestamp_lte: str | None = None
    refresh_interval: str | None = None
    relative_window_time: str | None = None
    y_axis_max_limit: int | None = None
    y_axis_min_limit: int | None = None
    config: dict[str, Any] | None = None
    chart_items: list[ChartItem] = []
    thresholds: list[Threshold] = []
    value_mappings: list[
        ExactMatchValueMapping | RangeValueMapping | RegexMatchValueMapping
    ] = []
    timezone: str | None = None


class Tab(SplightDatabaseBaseModel):
    id: str | None = None
    name: str
    charts: list[Chart] | None = None
    order: int | None = None
    dashboard: str


class Dashboard(SplightDatabaseBaseModel):
    id: str | None = None
    name: str
    description: str | None = Field(
        default=None, max_length=DESCRIPTION_MAX_LENGTH
    )
