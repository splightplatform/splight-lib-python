import random
from hexbytes import HexBytes

from splight_abstract import AbstractBlockchainClient, FunctionTransactError
from splight_models import CallResponse, Transaction


def get_random_hex(size: int = 256) -> HexBytes:
    return HexBytes(random.getrandbits(size))


class FakeBlockchainClient(AbstractBlockchainClient):

    def __init__(self, *args, **kwargs):
        pass

    def get_balance(self) -> int:
        return 111111111111111111

    def call(self, method: str, *args) -> CallResponse:
        return CallResponse(
            name=method,
            value=random.randint(0, 10000)
        )

    def transact(self, method: str, *args, **kwargs) -> Transaction:
        if method not in ["mint", "burn", "transfer"]:
            raise FunctionTransactError(method)

        return Transaction.parse_obj({
            "blockHash": get_random_hex(size=256),
            "blockNumber": 102812,
            "contractAddress": None,
            "cumulativeGasUsed": 40662,
            "from": get_random_hex(size=256),
            "gasUsed": 40662,
            "isPrivacyMarkerTransaction": False,
            "logsBloom": get_random_hex(size=1024),
            "status": 1,
            "to": get_random_hex(size=256),
            "transactionHash": get_random_hex(size=256),
            "transactionIndex": 0,
            "type": "0x0"
        })

    def get_transaction(self, tx_hash: HexBytes) -> Transaction:

        return Transaction.parse_obj({
            "blockHash": get_random_hex(size=256),
            "blockNumber": 102812,
            "contractAddress": None,
            "cumulativeGasUsed": 40662,
            "from": get_random_hex(size=256),
            "gasUsed": 40662,
            "isPrivacyMarkerTransaction": False,
            "logsBloom": get_random_hex(size=1024),
            "status": 1,
            "to": get_random_hex(size=256),
            "transactionHash": tx_hash,
            "transactionIndex": 0,
            "type": "0x0"
        })
