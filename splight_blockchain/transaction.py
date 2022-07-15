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


class BlockchainTransacction(BaseModel):
    nonce: int
    from_account: Optional[str] = Field(None, alias="from")
    to_account: Optional[str] = Field(None, alias="to")
    gas: int
    gas_price: int = Field(..., alias="gasPrice")
    chain_id: int = Field(DEFAULT_CHAIN_ID, alias="chainId")
    value: Optional[int] = None

    class Config:
        allow_population_by_field_name = True
