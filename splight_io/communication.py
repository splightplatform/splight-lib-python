from abc import ABCMeta, abstractmethod
from confluent_kafka import Consumer, Producer
from .settings import TOPIC, CONSUMER_CONFIG, PRODUCER_CONFIG, COMM_TYPE

import json


class Data:
    pass


class AbstractComunication(metaclass=ABCMeta):

    @abstractmethod
    def send(self):
        pass

    @abstractmethod
    def receive(self):
        pass


class ZeroQueueCommunication(AbstractComunication):
    def __init__(self, *args, **kwargs):
        self.client = None

    def send(self, data: Data):
        self.client.send(data)

    def receive(self) -> Data:
        return self.client.receive()


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
                print(msg.error())
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


communications = {'KAFKA': KafkaQueueCommunication}


class QueueCommunication(AbstractComunication):
    def __init__(self):
        self.queue = communications[COMM_TYPE]()

    def receive(self):
        return self.queue.receive()

    def send(self, data):
        self.queue.send(data)
