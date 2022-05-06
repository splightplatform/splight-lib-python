from .base import SplightBaseModel
from typing import List


class NetTarget(SplightBaseModel):
    ip: str
    port: int


class NetRule(SplightBaseModel):
    origin: NetTarget
    destination: NetTarget


class NetValue(SplightBaseModel):
    value: List[NetRule]

