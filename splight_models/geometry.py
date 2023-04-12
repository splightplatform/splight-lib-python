from splight_models.base import SplightBaseModel
from typing import List, Union


class Geometry(SplightBaseModel):
    type: str
    coordinates: List[Union[List[List[float]], List[float], float]]


class GeometryCollection(SplightBaseModel):
    type: str
    geometries: List[Geometry]
