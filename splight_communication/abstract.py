import json
from typing import Dict, ByteString
from abc import ABCMeta, abstractmethod


class AbstractCommunication(metaclass=ABCMeta):
    @staticmethod
    def _encode(data: Dict):
        return json.dumps(data).encode('utf-8')

    @staticmethod
    def _decode(data: ByteString):
        return json.loads(data.decode('utf-8'))

    @abstractmethod
    def send(self):
        pass

    @abstractmethod
    def receive(self):
        pass
