from typing import Any, Dict, List, Optional

from splight_lib.models.base import SplightDatabaseBaseModel


class Filter(SplightDatabaseBaseModel):
    id: Optional[str] = None
    chart_item: str
    operator: Optional[str]
    key: Optional[str]
    value: Optional[str]
    label: Optional[str]


class AdvancedFilter(SplightDatabaseBaseModel):
    id: Optional[str] = None
    chart_item: str
    operator: Optional[str]
    key: Optional[str]
    field: Optional[str]
    value: Optional[str]


class ChartItem(SplightDatabaseBaseModel):
    id: Optional[str] = None
    chart: str
    label: str
    order: Optional[int]
    color: Optional[str]
    position_x: Optional[str]
    position_y: Optional[str]
    width: Optional[str]
    height: Optional[str]
    split_by: Optional[str]
    aggregate_criteria: Optional[str]
    aggregate_period: Optional[str]
    source: Optional[str]
    source_label: Optional[str]
    source_type: Optional[str]  # TODO: define options (component, native)
    source_component_label: Optional[str]
    source_component_id: Optional[str]
    output_format: Optional[str]
    target: Optional[str]
    old_source: Optional[str]
    old_source_label: Optional[str]
    filters: Optional[List[Filter]]
    advanced_filters: Optional[List[AdvancedFilter]]
    query_params: Optional[str]


class Chart(SplightDatabaseBaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str]
    items: Optional[List[ChartItem]]
    tab: str
    position_x: Optional[str] = 0
    position_y: Optional[str] = 0
    height: Optional[str] = 28
    width: Optional[str] = 80
    min_height: Optional[str] = 14
    min_width: Optional[str] = 14
    type: Optional[str]
    timestamp_gte: Optional[str]
    timestamp_lte: Optional[str]
    refresh_interval: Optional[str]
    relative_window_time: Optional[str]
    external_resource: Optional[str]
    external_resource_type: Optional[str]
    y_axis_max_limit: Optional[str]
    y_axis_min_limit: Optional[str]
    config: Optional[Dict[str, Any]]


class Tab(SplightDatabaseBaseModel):
    id: Optional[str] = None
    name: str
    charts: Optional[List[Chart]]
    order: Optional[int]
    dashboard: str


class Dashboard(SplightDatabaseBaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str]
