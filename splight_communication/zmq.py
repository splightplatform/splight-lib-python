import zmq
import json
from typing import Dict, Any

from .settings import ZMQ_RECEIVER_PORT, ZMQ_SENDER_PORT
from .abstract import AbstractCommunication


class ZMQueueCommunication(AbstractCommunication):
    def __init__(self):
        context = zmq.Context()
        self.receiver = context.socket(zmq.PAIR)
        self.receiver.bind("tcp://*:{}".format(ZMQ_RECEIVER_PORT))

        self.sender = context.socket(zmq.PAIR)
        self.sender.connect("tcp://localhost:{}".format(ZMQ_SENDER_PORT))

    def send(self, data: dict) -> None:
        data: str = json.dumps(data)
        self.sender.send(data.encode("utf-8"))

    def receive(self) -> dict:
        msg = self.receiver.recv().decode('utf-8')
        data: Dict[str, Any] = json.loads(msg)
        return data
