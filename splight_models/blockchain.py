from typing import Any, Dict

from .base import SplightBaseModel


class SmartContract(SplightBaseModel):
    address: str
    abi: Dict[str, Any]
