from typing import Any, Dict, Union, List

from .base import SplightBaseModel


class SmartContract(SplightBaseModel):
    address: str
    abi: List[Dict[str, Any]]


class FunctionResponse(SplightBaseModel):
    name: str
    value: Union[int, float, str]
