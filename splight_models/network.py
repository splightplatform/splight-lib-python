from pydantic import BaseModel
from typing import Optional
from enum import Enum


class Network(BaseModel):
    id: Optional[str]
    name: str
    username: Optional[str]
    password: Optional[str]
    file: Optional[str]
