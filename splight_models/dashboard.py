from .base import SplightBaseModel
from typing import Optional, List


class Dashboard(SplightBaseModel):
    id: Optional[str]
    name: str
    description: Optional[str] = None


class Tab(SplightBaseModel):
    id: Optional[str]
    dashboard_id: str
    name: str


class Filter(SplightBaseModel):
    id: Optional[str]
    chart_item_id: str
    operator: str = "eq"  # eg. eq, gt, gte, lt
    key: str              # asset_id
    value: str            # 5


class ChartItem(SplightBaseModel):
    id: Optional[str]
    chart_id: str
    color: Optional[str]
    position_x: Optional[str]
    position_y: Optional[str]
    width: Optional[int]
    height: Optional[int]
    source: Optional[str]
    target: Optional[str]
    split_by: Optional[str]
    label: Optional[str]


class Chart(SplightBaseModel):
    id: Optional[str]
    name: Optional[str]
    description: Optional[str] = None
    tab_id: str
    type: str
    position: Optional[str]
    timestamp_gte: Optional[str] = None
    timestamp_lte: Optional[str] = None
    refresh_interval: Optional[str] = None
    relative_window_time: Optional[str] = None
    aggregate_criteria: Optional[str] = None
    aggregate_period: Optional[str] = None
    external_resource: Optional[str] = None
    external_resource_type: Optional[str] = None
