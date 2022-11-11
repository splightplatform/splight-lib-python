from splight_abstract import AbstractBlockchainClient, AbstractRemoteClient
from remote_splight_lib.auth import SplightAuthToken
from remote_splight_lib.settings import settings
from splight_models import Transaction, BlockchainContract
from furl import furl
from requests import Session
from typing import Dict
from hexbytes import HexBytes
import json


class BlockchainClient(AbstractBlockchainClient, AbstractRemoteClient):
    _PREFIX = "blockchain"

    def __init__(self, namespace: str = "default") -> None:
        super().__init__()
        super(BlockchainClient, self).__init__(namespace=namespace)
        self._base_url = furl(settings.SPLIGHT_PLATFORM_API_HOST)
        token = SplightAuthToken(
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
        )
        self._session = Session()
        self._session.headers.update(token.header)

    def transact(self, method: str, private_key: str, contract_address: str, **kwargs) -> Dict:
        # POST /blockchain/contract/{contract.address}/transact/{method}
        url = self._base_url / f"{self._PREFIX}/contract/{contract_address}/transact/{method}/"
        data = {"private_key": private_key, **kwargs}
        response = self._session.post(url, json=data)
        response.raise_for_status()
        return response

    def call(self, method: str, *args) -> Dict:
        return super().call(method, *args)

    def get_balance(self) -> int:
        return super().get_balance()

    def get_transaction(self, tx_hast: HexBytes) -> Dict:
        return super().get_transaction(tx_hast)
