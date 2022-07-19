from abc import abstractmethod

from web3.datastructures import AttributeDict

from client import AbstractClient


class BlockchainClient(AbstractClient):
    @abstractmethod
    def call(self, method: str, *args):
        pass

    @abstractmethod
    def transact(self, method: str, *args, **kwargs) -> AttributeDict:
        pass
