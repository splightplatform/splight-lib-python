import zmq
import json
from typing import Dict, Any

from .settings import ZMQ_RECEIVER_PORT, ZMQ_SENDER_PORT
from .abstract import AbstractCommunication


class ZMQueueCommunication(AbstractCommunication):
    def __init__(self, reverse=False, *args, **kwargs):
        recv_port, sender_port = ZMQ_RECEIVER_PORT, ZMQ_SENDER_PORT
        if reverse:
            recv_port, sender_port = ZMQ_SENDER_PORT, ZMQ_RECEIVER_PORT

        context = zmq.Context()
        self.receiver = context.socket(zmq.PAIR)
        self.receiver.bind("tcp://*:{}".format(recv_port))

        self.sender = context.socket(zmq.PAIR)
        self.sender.connect("tcp://localhost:{}".format(sender_port))

    def send(self, data: dict) -> None:
        data: str = json.dumps(data)
        self.sender.send(data.encode("utf-8"))

    def receive(self) -> dict:
        msg = self.receiver.recv().decode('utf-8')
        data: Dict[str, Any] = json.loads(msg)
        return data
