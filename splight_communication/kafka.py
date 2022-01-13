
from typing import ByteString, Dict
from confluent_kafka import Consumer, Producer
import json

from .settings import CONFLUENT_TOPIC, CONFLUENT_CONSUMER_CONFIG, CONFLUENT_PRODUCER_CONFIG
from .abstract import AbstractCommunication


class KafkaQueueCommunication(AbstractCommunication):
    def __init__(self, topic: str = 'default'):
        self.topic = topic
        self.consumer = Consumer(CONFLUENT_CONSUMER_CONFIG)
        self.consumer.subscribe([self.topic])
        self.producer = Producer(CONFLUENT_PRODUCER_CONFIG)

    @staticmethod
    def _encode(data: Dict):
        return json.dumps(data).encode('utf-8')

    @staticmethod
    def _decode(data: ByteString):
        return json.loads(data.decode('utf-8'))

    def receive(self):
        msg = self.consumer.consume(num_messages=1, timeout=-1)[0]
        if msg.error():
            # TODO do something more specific
            raise Exception(msg.error())
        data = msg.value()
        return self._decode(data)

    def send(self, data: Dict) -> None:
        self.producer.produce(self.topic, value=self._encode(data))
        self.producer.flush()
