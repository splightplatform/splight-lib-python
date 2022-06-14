from typing import List, Optional
from .base import SplightBaseModel


class Graph(SplightBaseModel):
    id: Optional[str]
    title: str
    modifiable: bool


class Node(SplightBaseModel):
    id: Optional[str]
    type: str
    graph_id: str
    asset_id: str


class Edge(SplightBaseModel):
    id: Optional[str]
    directed: bool
    graph_id: str
    source_id: str
    target_id: str
