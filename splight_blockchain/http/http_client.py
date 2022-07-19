import json
from typing import Optional

from eth_account import Account
from hexbytes import HexBytes
from web3 import Web3
from web3.contract import ContractFunction
from web3.middleware import geth_poa_middleware

from splight_models.blockchain import (
    FunctionResponse,
    SmartContract,
    Transaction,
)

from splight_blockchain.abstract import BlockchainClient
from splight_blockchain.exceptions import (
    ContractNotLoaded,
    FunctionCallError,
    MethodNotAllowed,
    ProviderConnectionError,
    TransactionError,
)
from .settings import ProviderSchemas, blockchain_config


class HTTPClient(BlockchainClient):

    _POA_MIDDLEWARE_LAYER = 0

    def __init__(
        self,
        account: str,
        host: str = blockchain_config.PROVIDER,
        port: str = blockchain_config.PORT,
        schema: ProviderSchemas = blockchain_config.SCHEMA,
        signing_address: str = blockchain_config.SPLIGHT_ADDRESS,
        signing_key: str = blockchain_config.SPLIGHT_PRIVATE_KEY,
    ):
        super().__init__()
        provider = Web3.HTTPProvider(f"{schema}://{host}:{port}")
        self._connection = Web3(provider)

        self._connection.middleware_onion.inject(
            geth_poa_middleware, layer=self._POA_MIDDLEWARE_LAYER
        )
        self._signing_account = Account.from_key(signing_key)

        self._account_address = account

        if not self._connection.isConnected():
            raise ProviderConnectionError

        self._contract = None

    @property
    def contract(self) -> Optional[SmartContract]:
        """Gets the smart contract in use

        Returns
        -------
        Optional[SmartContract]
            The smart contract
        """
        if self._contract:
            return SmartContract(
                address=self._contract.address,
                abi=json.loads(self._contract.abi),
            )
        return None

    @contract.setter
    def contract(self, contract: SmartContract):
        self._contract = self._connection.eth.contract(
            address=contract.address, abi=contract.abi
        )

    def to_ether(self, amount: float):
        return self._connection.toWei(amount, "ether")

    def from_ether(self, amount: float):
        return self._connection.fromWei(amount, "ether")

    def get_balance(self):
        return self._connection.eth.get_balance(self._account_address)

    def call(
        self, method: str, *args, use_account: bool = False
    ) -> FunctionResponse:

        if not self._contract:
            raise ContractNotLoaded()

        try:
            function_callable = self._contract.get_function_by_name(method)
        except ValueError as exc:
            raise MethodNotAllowed(method) from exc

        full_args = args
        if use_account:
            full_args = (self._account_address, *full_args)
        try:
            output = function_callable(*full_args).call()
        except TypeError as exc:
            raise FunctionCallError(method) from exc
        return FunctionResponse(name=method, value=output)

    def transact(self, method: str, *args, **kwargs) -> Transaction:
        if not self._contract:
            raise ContractNotLoaded()
        _method = getattr(self, f"_{method}", None)
        if not _method:
            raise MethodNotAllowed(method)
        output = _method(*args, **kwargs)
        return output

    def _mint(
        self, amount: int = 0, metadata: str = "", gas: int = 21000
    ) -> Transaction:
        function_callable = self._contract.functions.mint
        function = function_callable(self._account_address, amount, metadata)
        return self._sign_and_send_transaction(function, gas=gas)

    def _burn(
        self, amount: int = 0, metadata: str = "", gas: int = 21000
    ) -> Transaction:
        function_callable = self._contract.functions.burn
        function = function_callable(self._account_address, amount, metadata)
        return self._sign_and_send_transaction(function, gas=gas)

    def _transfer(
        self, dst_address: str, amount: int, gas: int = 21000
    ) -> Transaction:
        function_callable = self._contract.functions.transferFrom
        function = function_callable(
            self._account_address, dst_address, amount
        )
        return self._sign_and_send_transaction(function, gas=gas)

    def _sign_and_send_transaction(
        self, builder: ContractFunction, gas: int = 21000
    ) -> Transaction:

        nonce = self._connection.eth.get_transaction_count(
            self._signing_account.address
        )
        tx = {
            "from": self._signing_account.address,
            "nonce": nonce,
            "gas": gas,
            "gasPrice": 0,
        }
        transaction = builder.build_transaction(tx)
        signed = self._connection.eth.account.sign_transaction(
            transaction, self._signing_account.privateKey
        )
        tx_hash = self._connection.eth.send_raw_transaction(
            signed.rawTransaction
        )
        receipt = self._connection.eth.wait_for_transaction_receipt(tx_hash)

        if not receipt.status:
            raise TransactionError(tx_hash.hex())

        return Transaction.parse_obj(receipt)

    def get_transaction(self, tx_hash: HexBytes) -> Transaction:
        """Returns a made transaction.

        Parameters
        ----------
        tx_hash : HexBytes
            The hash of the transaction to be recovered.

        Returns
        -------
        Transaction
            The transaction information
        """
        tx = self._connection.eth.get_transaction(tx_hash)
        return Transaction.parse_obj(tx)

    def get_transaction_receipt(self, tx_hash: HexBytes) -> Transaction:
        """Gets the receipt of a transaction

        Parameters
        ----------
        tx_hash : HexBytes
            The hash of the transaction.

        Returns
        -------
        Transaction
            The receipt dict of the transaction
        """
        tx_receipt = self._connection.eth.get_transaction_receipt(tx_hash)
        return Transaction.parse_obj(tx_receipt)
