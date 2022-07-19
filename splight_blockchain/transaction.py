from typing import Dict, Optional, Protocol

from pydantic import BaseModel, Field

from .default import DEFAULT_CHAIN_ID


class TransactionBuilder(Protocol):
    """Interface for a Blockchain Transaction Builder"""

    def build_transaction(self, transaction: Dict) -> Dict:
        """Buils a transaction

        Parameters
        ----------
        transaction : Dict
            The dictionary with the transaction

        Returns
        -------
        Dict
            The built transaction with full information of the transaction.
        """
        ...


class Transaction(BaseModel):
    from_account: Optional[str] = Field(None, alias="from")
    to_account: Optional[str] = Field(None, alias="to")
    gas: int
    max_fee_per_gas: Optional[int] = Field(None, alias="maxFeePerGas")
    max_priority_fee_per_gas: Optional[int] = Field(
        None, alias="maxPriorityFeePerGas"
    )
    gas_price: int = Field(..., alias="gasPrice")
    value: Optional[int] = None
    data: Optional[str] = None
    nonce: int
    chain_id: int = Field(DEFAULT_CHAIN_ID, alias="chainId")

    class Config:
        allow_population_by_field_name = True
