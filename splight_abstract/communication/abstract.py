import json
from typing import Dict, ByteString
from abc import abstractmethod
from splight_abstract.client import AbstractClient


class AbstractCommunication(AbstractClient):
    @staticmethod
    def _encode(data: Dict):
        return json.dumps(data, default=str).encode('utf-8')

    @staticmethod
    def _decode(data: ByteString):
        return json.loads(data.decode('utf-8'))

    @abstractmethod
    def send(self, data: Dict) -> None:
        pass

    @abstractmethod
    def receive(self) -> Dict:
        pass
