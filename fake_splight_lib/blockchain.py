import random
from hexbytes import HexBytes

from splight_blockchain.abstract import BlockchainClient
from splight_blockchain.exceptions import MethodNotAllowed
from splight_models import CallResponse, Transaction


def get_random_hex(size: int = 256) -> HexBytes:
    return HexBytes(random.getrandbits(size))


class FakeBlockchainClient(BlockchainClient):

    def call(self, method: str, *args) -> CallResponse:
        return CallResponse(
            name=method,
            value=random.randint(0, 10000)
        )

    def transact(self, method: str, *args, **kwargs) -> Transaction:
        if method not in ["mint", "burn", "transfer"]:
            raise MethodNotAllowed(method)

        return {
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
        }

    def get_transaction(self, tx_hash: HexBytes) -> Transaction:

        return Transaction(**{
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

    def get_transaction_receipt(self, tx_hash: HexBytes) -> Transaction:

        return Transaction(**{
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
