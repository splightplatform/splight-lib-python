import zmq
from typing import Dict

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
        self.sender.send(self._encode(data))

    def receive(self) -> Dict:
        data = self.receiver.recv()
        return self._decode(data)