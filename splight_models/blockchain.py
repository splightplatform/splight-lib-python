# TODO remove this models from here.
import re
import json
from datetime import datetime, timezone
from typing import Optional, Union
from pydantic import validator, Json, Field, validator
from hexbytes import HexBytes
from splight_models.base import SplightBaseModel


class BlockchainContractSubscription(SplightBaseModel):
    id: Optional[str]
    asset_id: str
    attribute_id: str
    contract_id: str
    last_checkpoint: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BlockchainContract(SplightBaseModel):
    id: Optional[str]
    name: str
    description: str = ""
    address: str
    abi_json: Json

    @validator('address', pre=True, always=True)
    def set_account_id_now(cls, v):
        regex = r"(\b0x[a-fA-F0-9]{40}\b)"
        assert re.match(regex, v), 'Account value not allowed it should be a hex str.'
        return v

    @validator('abi_json', pre=True, always=True)
    def set_abi_json_now(cls, v):
        if isinstance(v, list):
            return json.dumps(v)
        return v


class CallResponse(SplightBaseModel):
    name: str
    value: Union[int, float, str]


class Transaction(SplightBaseModel):
    from_account: str = Field(..., alias="from")
    to_account: Optional[str] = Field(None, alias="to")
    status: Optional[int] = 0
    contract_address: Optional[str] = Field(None, alias="contractAddress")
    block_hash: str = Field(..., alias="blockHash")
    block_number: int = Field(..., alias="blockNumber")
    transaction_hash: str = Field(..., alias="transactionHash")
    transaction_index: int = Field(..., alias="transactionIndex")

    @validator("from_account", "to_account", "block_hash", "transaction_hash", "contract_address", pre=True)
    def cast_to_str(cls, value):
        return value.hex() if isinstance(value, HexBytes) else value
