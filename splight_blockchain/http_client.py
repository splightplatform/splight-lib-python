from dataclasses import dataclass
from typing import Optional

from eth_account.datastructures import SignedTransaction
from pydantic import BaseModel, Field
from web3 import Web3
from web3.middleware import geth_poa_middleware

from .default import DEFAULT_CHAIN_ID, DEFAULT_GAS_LIMIT, DEFAULT_GAS_PRICE
from .settings import ProviderSchemas, blockchain_config


class ProviderConnectionError(Exception):
    def __init__(self):
        self._msg = "Unable to connect to provider"

    def __str__(self) -> str:
        return self._msg


@dataclass
class BlockchainAccount:
    address: str
    private_key: str


class BlockchainTransacction(BaseModel):
    nonce: int
    from_account: Optional[str] = Field(None, alias="from")
    to_account: Optional[str] = Field(None, alias="to")
    gas: int
    gas_price: int = Field(..., alias="gasPrice")
    chain_id: int = Field(DEFAULT_CHAIN_ID, alias="chainId")
    value: int

    class Config:
        allow_population_by_field_name = True


class HTTPClient:

    _POA_MIDDLEWARE_LAYER = 0

    def __init__(
        self,
        provider_host: str = blockchain_config.PROVIDER,
        provider_port: int = blockchain_config.PORT,
        schema: ProviderSchemas = blockchain_config.SCHEMA,
    ):
        """Class constructor

        Parameters
        ----------
        provider_host : str
            Provider's host
        provider_port : int
            Provider's port
        schema : ProviderSchemas
            Schema to be used

        Raises
        ------
        ProviderConnectionError thrown when there is a problem in the
            connection
        """
        provider = Web3.HTTPProvider(
            f"{schema}://{provider_host}:{provider_port}"
        )
        self._connection = Web3(provider)

        self._connection.middleware_onion.inject(
            geth_poa_middleware, layer=self._POA_MIDDLEWARE_LAYER
        )

        if not self._connection.isConnected():
            raise ProviderConnectionError

    def transfer(
        self,
        from_account: BlockchainAccount,
        to_account: BlockchainAccount,
        amount: int,
    ):
        """Transfer a crypto coin from one account to another.

        Parameters
        ----------
        from_account : BlockchainAccount
            Account that sends the amount of crypto coins
        to_account : BlockchainAccount
            The account that receives the crypto coins
        amount : int
            The amount of coins that are being transferred.
        """
        nonce = self._connection.eth.get_transaction_count(
            from_account.address
        )
        transaction = BlockchainTransacction(
            nonce=nonce,
            to_account=to_account.address,
            gas=DEFAULT_GAS_LIMIT,
            gas_price=DEFAULT_GAS_PRICE,
            value=self._connection.toWei(amount, "ether"),
        )

        signed = self._sign_transaction(from_account, transaction)
        self._connection.eth.send_raw_transaction(signed.rawTransaction)

    def _sign_transaction(
        self, account: BlockchainAccount, transaction: BlockchainTransacction
    ) -> SignedTransaction:
        """Signs a blockchain transaction

        Parameters
        ----------
        account : BlockchainAccount
            The account that signs the transaction
        transaction : BlockchainTransacction
            The transaction to by signed

        Returns
        -------
        SignedTransaction
            The signed transaction
        """
        signed = self._connection.eth.account.sign_transaction(
            transaction.dict(by_alias=True, exclude_none=True),
            account.private_key,
        )
        return signed
