from abc import ABCMeta, abstractmethod
from confluent_kafka import Consumer, Producer
from .settings import TOPIC, CONSUMER_CONFIG, PRODUCER_CONFIG, COMM_TYPE
from .settings import DEFAULT_RECEIVER_PORT, DEFAULT_SENDER_PORT
from typing import Dict, Any
import zmq
import json


class AbstractComunication(metaclass=ABCMeta):

    @abstractmethod
    def send(self):
        pass

    @abstractmethod
    def receive(self):
        pass


class FakeQueueCommunications(AbstractComunication):
    def send(self, data: dict):
        pass

    def receive(self) -> dict:
        return {'data': 'test'}


class KafkaQueueCommunication(AbstractComunication):
    def __init__(self):
        self.consumer = Consumer(CONSUMER_CONFIG)
        self.consumer.subscribe([TOPIC])
        self.producer = Producer(PRODUCER_CONFIG)

    def receive(self):
        data = None
        while True:
            msg = self.consumer.poll(1.0)

            if msg is None:
                pass
            elif msg.error():
                # TODO do something
                pass
            else:
                # Check for Kafka message
                record_value = msg.value()
                data = json.loads(record_value)
                break
        return data

    def send(self, data: dict) -> None:
        self.producer.produce(TOPIC, key=b'0', value=data)
        self.producer.flush()


class ZMQueueCommunication(AbstractComunication):
    def __init__(self):
        context = zmq.Context()
        self.resiver = context.socket(zmq.PAIR)
        self.resiver.bind("tcp://*:{}".format(DEFAULT_RECEIVER_PORT))

        self.sender = context.socket(zmq.PAIR)
        self.sender.connect("tcp://localhost:{}".format(DEFAULT_SENDER_PORT))

    def send(self, data: dict) -> None:
        data: str = json.dumps(data)
        self.sender.send(data.encode("utf-8"))

    def receive(self) -> dict:
        msg = self.resiver.recv().decode('utf-8')
        data: Dict[str, Any] = json.loads(msg)
        return data


communications = {
    "ZMQ": ZMQueueCommunication,
    'KAFKA': KafkaQueueCommunication,
    'FAKE': FakeQueueCommunications
}


class QueueCommunication(AbstractComunication):
    def __init__(self, queue_type: str = COMM_TYPE):
        self.queue = communications[queue_type]()

    def receive(self):
        return self.queue.receive()

    def send(self, data):
        self.queue.send(data)
