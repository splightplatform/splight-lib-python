from dataclasses import dataclass
from typing import Optional

from eth_account.datastructures import SignedTransaction
from web3 import Web3
from web3.middleware import geth_poa_middleware

from .default import DEFAULT_GAS_LIMIT, DEFAULT_GAS_PRICE
from .exceptions import (
    LoadContractError,
    ProviderConnectionError,
    TransactionNotAllowed,
)
from .settings import ProviderSchemas, blockchain_config
from .transaction import TransactionBuilder, BlockchainTransacction


@dataclass
class BlockchainAccount:
    address: str
    private_key: str


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

        self._contract = None

    def load_contract(self, contract_address: str, contract_abi_path: str):
        """Loads a custom contrat defined in a JSON file and the contract
        address.

        Parameters
        ----------
        contract_address : str
            The hash for the contract.
        contract_abi_path : str
            The path to the JSON file with the contract.

        Raises
        ------
        LoadContractError when there is any error loading the contract.
        """
        with open(contract_abi_path, "r") as fid:
            contract_abi = fid.read()

        contract_abi = contract_abi.translate(
            str.maketrans({"\n": "", "\t": ""})
        )

        try:
            self._contract = self._connection.eth.contract(
                address=contract_address, abi=contract_abi
            )
        except Exception as exc:
            self._contract = None
            raise LoadContractError(
                contract_address, contract_abi_path
            ) from exc

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

    def mint(self, account: BlockchainAccount, metadata: str):
        """Makes a mint transaction if it's allowed.

        Parameters
        ----------
        account : BlockchainAccount
            The account that is minting.
        metadata : str
            The metada for the transaction

        Raises
        ------
        TransactionNotAllowed thrown when the mint operation is not allowed.
        """
        if not self._contract:
            raise TransactionNotAllowed(transaction_name="mint")
        mint = self._contract.functions.mint(account.address, metadata)
        transaction = BlockchainTransacction(
            from_account=account.address,
            nonce=self._connection.eth.get_transaction_count(account.address),
            gas=210000,
            gas_price=DEFAULT_GAS_PRICE,
        )
        signed = self._sign_transaction(account, transaction, builder=mint)
        trn_hash = self._connection.eth.send_raw_transaction(
            signed.rawTransaction
        )
        self._connection.eth.wait_for_transaction_receipt(trn_hash)

    def burn(self, account: BlockchainAccount):
        if not self._contract:
            raise TransactionNotAllowed(transaction_name="burn")
        __import__("ipdb").set_trace()
        burn = self._contract.functions.burn(account.address)
        transaction = BlockchainTransacction(
            from_account=account.address,
            nonce=self._connection.eth.get_transaction_count(account.address),
            gas=0,
            gas_price=DEFAULT_GAS_PRICE,
        )
        __import__("ipdb").set_trace()
        signed = self._sign_transaction(account, transaction, builder=burn)
        trn_hash = self._connection.eth.send_raw_transaction(
            signed.rawTransaction
        )
        response = self._connection.eth.wait_for_transaction_receipt(trn_hash)
        print(response)

    def _sign_transaction(
        self,
        account: BlockchainAccount,
        transaction: BlockchainTransacction,
        builder: Optional[TransactionBuilder] = None,
    ) -> SignedTransaction:
        """Signs a blockchain transaction

        Parameters
        ----------
        account : BlockchainAccount
            The account that signs the transaction
        transaction : BlockchainTransacction
            The transaction to by signed
        builder : Optional[TransactionBuilder]
            The transaction builder

        Returns
        -------
        SignedTransaction
            The signed transaction
        """
        built_transaction = transaction.dict(by_alias=True, exclude_none=True)
        if builder:
            built_transaction = builder.build_transaction(
                transaction.dict(by_alias=True, exclude_none=True)
            )
        signed = self._connection.eth.account.sign_transaction(
            built_transaction,
            account.private_key,
        )
        return signed
