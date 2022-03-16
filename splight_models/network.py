from pydantic import BaseModel
from typing import Optional, List


class NetTarget(BaseModel):
    ip: str
    port: int


class NetRule(BaseModel):
    origin: NetTarget
    destination: NetTarget


class NetValue(BaseModel):
    value: List[NetRule]


class Network(BaseModel):
    id: Optional[str]
    name: str
    description: Optional[str] = None
    username: Optional[str]
    password: Optional[str]
    file_id: Optional[str]
