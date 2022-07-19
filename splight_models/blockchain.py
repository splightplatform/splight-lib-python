from typing import Any, Dict, List, Optional, Union

from pydantic import Field, validator

from .base import SplightBaseModel

from hexbytes import HexBytes


class SmartContract(SplightBaseModel):
    address: str
    abi: List[Dict[str, Any]]


class FunctionResponse(SplightBaseModel):
    name: str
    value: Union[int, float, str]


class Transaction(SplightBaseModel):
    from_account: str = Field(..., alias="from")
    to_account: Optional[str] = Field(None, alias="to")
    status: Optional[int] = 0
    contract_address: Optional[str] = Field(..., alias="contractAddress")
    block_hash: bytes = Field(..., alias="blockHash")
    block_number: int = Field(..., alias="blockNumber")
    transaction_hash: str = Field(..., alias="transactionHash")
    transaction_index: int = Field(..., alias="transactionIndex")

    @validator("block_hash", "transaction_hash", "contract_address", pre=True)
    def cast_to_str(cls, value):
        return value.hex() if isinstance(value, HexBytes) else value
