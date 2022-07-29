import os

from fake_splight_lib.blockchain import FakeBlockchainClient
from splight_blockchain.http.http_client import HTTPClient


REGISTRY = {
    "fake": FakeBlockchainClient,
    "http": HTTPClient
}

BlockchainClient = REGISTRY.get(os.environ.get("BLOCKCHAIN", "fake"))
