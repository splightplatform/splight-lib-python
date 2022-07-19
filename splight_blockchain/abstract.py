from abc import abstractmethod

from hexbytes import HexBytes
from web3.datastructures import AttributeDict

from client import AbstractClient


class BlockchainClient(AbstractClient):

    @abstractmethod
    def get_balance(self):
        pass

    @abstractmethod
    def call(self, method: str, *args):
        pass

    @abstractmethod
    def transact(self, method: str, *args, **kwargs) -> AttributeDict:
        pass

    @abstractmethod
    def get_transaction(self, tx_hast: HexBytes) -> AttributeDict:
        pass

    @abstractmethod
    def get_transaction_receipt(self, tx_hast: HexBytes) -> AttributeDict:
        pass
