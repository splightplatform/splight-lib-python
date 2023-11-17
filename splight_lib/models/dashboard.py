from typing import Any, Dict, List, Optional

from pydantic import Field

from splight_lib.constants import DESCRIPTION_MAX_LENGTH
from splight_lib.models.base import SplightDatabaseBaseModel


class Filter(SplightDatabaseBaseModel):
    id: Optional[str] = None
    chart_item: str
    operator: Optional[str] = None
    key: Optional[str] = None
    value: Optional[str] = None
    label: Optional[str] = None


class AdvancedFilter(SplightDatabaseBaseModel):
    id: Optional[str] = None
    chart_item: str
    operator: Optional[str] = None
    key: Optional[str] = None
    field: Optional[str] = None
    value: Optional[str] = None


class ChartItem(SplightDatabaseBaseModel):
    id: Optional[str] = None
    chart: str
    label: str
    order: Optional[int] = None
    color: Optional[str] = None
    position_x: Optional[str] = None
    position_y: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None
    split_by: Optional[str] = None
    aggregate_criteria: Optional[str] = None
    aggregate_period: Optional[str] = None
    source: Optional[str] = None
    source_label: Optional[str] = None
    source_type: Optional[
        str
    ] = None  # TODO: define options (component, native)
    source_component_label: Optional[str] = None
    source_component_id: Optional[str] = None
    output_format: Optional[str] = None
    target: Optional[str] = None
    old_source: Optional[str] = None
    old_source_label: Optional[str] = None
    filters: Optional[List[Filter]] = None
    advanced_filters: Optional[List[AdvancedFilter]] = None
    query_params: Optional[str] = None


class Chart(SplightDatabaseBaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = Field(
        default=None, max_length=DESCRIPTION_MAX_LENGTH
    )
    items: Optional[List[ChartItem]] = None
    tab: str
    position_x: Optional[str] = 0
    position_y: Optional[str] = 0
    height: Optional[str] = 28
    width: Optional[str] = 80
    min_height: Optional[str] = 14
    min_width: Optional[str] = 14
    type: Optional[str] = None
    timestamp_gte: Optional[str] = None
    timestamp_lte: Optional[str] = None
    refresh_interval: Optional[str] = None
    relative_window_time: Optional[str] = None
    external_resource: Optional[str] = None
    external_resource_type: Optional[str] = None
    y_axis_max_limit: Optional[str] = None
    y_axis_min_limit: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class Tab(SplightDatabaseBaseModel):
    id: Optional[str] = None
    name: str
    charts: Optional[List[Chart]] = None
    order: Optional[int] = None
    dashboard: str


class Dashboard(SplightDatabaseBaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = Field(
        default=None, max_length=DESCRIPTION_MAX_LENGTH
    )
