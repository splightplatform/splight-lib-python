import json

from typing import Dict, ByteString
from client import AbstractClient
from abc import abstractmethod


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
