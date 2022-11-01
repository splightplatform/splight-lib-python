from typing import Optional
from .base import SplightBaseModel


class Graph(SplightBaseModel):
    id: Optional[str]
    title: str
    description: Optional[str] = None
    locked: bool = False


class Node(SplightBaseModel):
    id: Optional[str]
    type: str
    graph_id: str
    asset_id: Optional[str] = None
    color: str
    fill_color: Optional[str]
    position_x: int
    position_y: int
    width: str
    height: str

class Edge(SplightBaseModel):
    id: Optional[str]
    directed: bool
    graph_id: str
    asset_id: Optional[str] = None
    source_id: str
    target_id: str
    color: str
    source_handle: str
    target_handle: str
