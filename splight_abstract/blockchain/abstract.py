from abc import abstractmethod, ABC
from hexbytes import HexBytes
from splight_models.blockchain import CallResponse, Transaction, BlockchainContract


class AbstractBlockchainClient(ABC):

    @abstractmethod
    def get_balance(self) -> int:
        pass

    @abstractmethod
    def call(self, method: str, *args) -> CallResponse:
        pass

    @abstractmethod
    def transact(self, method: str, contract: BlockchainContract, *args, **kwargs) -> Transaction:
        pass

    @abstractmethod
    def get_transaction(self, tx_hast: HexBytes) -> Transaction:
        pass
