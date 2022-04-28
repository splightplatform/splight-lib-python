from pydantic import BaseModel
from typing import List


class NetTarget(BaseModel):
    ip: str
    port: int


class NetRule(BaseModel):
    origin: NetTarget
    destination: NetTarget


class NetValue(BaseModel):
    value: List[NetRule]

