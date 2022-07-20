from eth_account import Account
from hexbytes import HexBytes
from web3 import Web3
from web3.contract import ContractFunction
from web3.middleware import geth_poa_middleware

from splight_models.blockchain import (
    CallResponse,
    BlockchainContract,
    Transaction,
)

from splight_blockchain.abstract import AbstractBlockchainClient
from splight_blockchain.exceptions import (
    ContractNotLoaded,
    FunctionCallError,
    FunctionTransactError,
    ProviderConnectionError,
    TransactionError,
)
from .settings import blockchain_config


class HTTPClient(AbstractBlockchainClient):
    _POA_MIDDLEWARE_LAYER = 0
<<<<<<< HEAD
    _GAS = 210000
=======
    _GAS = 21000
>>>>>>> aece67d (Rebase)
    _contract = None

    def __init__(self, account: str):
        super().__init__()
        provider = Web3.HTTPProvider(blockchain_config.BLOCKCHAIN_RPC_URL)
        
        self._connection = Web3(provider)
        self._connection.middleware_onion.inject(
            geth_poa_middleware, layer=self._POA_MIDDLEWARE_LAYER
        )
        if not self._connection.isConnected():
            raise ProviderConnectionError

        self._account_address = account
        self._signing_account = Account.from_key(
            blockchain_config.BLOCKCHAIN_PRIVATE_KEY
        )

    @property
    def contract(self):
        return self._contract

    @contract.setter
    def contract(self, contract: BlockchainContract):
        self._contract = self._connection.eth.contract(
            address=contract.address,
            abi=contract.abi_json
        )

    @property
    def _nonce(self):
        return self._connection.eth.get_transaction_count(
            self._signing_account.address
        )

    def to_ether(self, amount: float):
        return self._connection.toWei(amount, "ether")

    def from_ether(self, amount: float):
        return self._connection.fromWei(amount, "ether")

    def get_balance(self):
        return self._connection.eth.get_balance(self._account_address)

    def call(self, method: str, *args) -> CallResponse:

        if not self._contract:
            raise ContractNotLoaded()

        try:
            _call = self._contract.get_function_by_name(method)
            output = _call(*args).call()
        except (ValueError, TypeError) as exc:
            raise FunctionCallError(method) from exc
    
        return CallResponse(name=method, value=output)

    def transact(self, method: str, *args, **kwargs) -> Transaction:
        if not self._contract:
            raise ContractNotLoaded()

        _transact = getattr(self, f"_{method}", None)
        if not _transact:
            raise FunctionTransactError(method)

        output = _transact(*args, **kwargs)
        return output

    def _mint(self, amount: int, metadata: str = "") -> Transaction:
        function = self._contract.functions.mintFrom(
            self._account_address,
            amount,
            metadata
        )
        return self._sign_and_send_transaction(function)

    def _burn(self, amount: int, metadata: str = "") -> Transaction:
        function = self._contract.functions.burnFrom(
            self._account_address,
            amount,
            metadata
        )
        return self._sign_and_send_transaction(function)

    def _transfer(self, dst_address: str, amount: int) -> Transaction:
        function = self._contract.functions.transferFrom(
            self._account_address,
            dst_address,
            amount
        )
        return self._sign_and_send_transaction(function)

    def _sign_and_send_transaction(self, function: ContractFunction) -> Transaction:
        tx = function.build_transaction({
            "from": self._signing_account.address,
            "nonce": self._nonce,
            "gas": self._GAS,
            "gasPrice": 0,
        })
        tx_signed = self._connection.eth.account.sign_transaction(
            tx, self._signing_account.privateKey
        )
        tx_hash = self._connection.eth.send_raw_transaction(
            tx_signed.rawTransaction
        )
        tx_receipt = self._connection.eth.wait_for_transaction_receipt(tx_hash)
        if not tx_receipt.status:
            raise TransactionError(tx_hash.hex())
        return Transaction.parse_obj(tx_receipt)

    def get_transaction(self, tx_hash: HexBytes) -> Transaction:
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
