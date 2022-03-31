from pydantic import BaseModel
from typing import Optional, List


class Dashboard(BaseModel):
    id: Optional[str]
    name: str
    description: Optional[str] = None


class Tab(BaseModel):
    id: Optional[str]
    dashboard_id: str
    name: str


class Filter(BaseModel):
    operator: str = "eq"  # eg. eq, gt, gte, lt
    key: str              # asset_id
    value: str            # 5


class Chart(BaseModel):
    id: Optional[str]
    tab_id: str
    type: str
    filters: List[Filter] = []
    refresh_interval: Optional[str] = None
    relative_window_time: Optional[str] = None
