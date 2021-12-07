
from confluent_kafka import Consumer, Producer
import json

from .settings import CONFLUENT_TOPIC, CONFLUENT_CONSUMER_CONFIG, CONFLUENT_PRODUCER_CONFIG
from .abstract import AbstractCommunication


class KafkaQueueCommunication(AbstractCommunication):
    def __init__(self):
        self.consumer = Consumer(CONFLUENT_CONSUMER_CONFIG)
        self.consumer.subscribe([CONFLUENT_TOPIC])
        self.producer = Producer(CONFLUENT_PRODUCER_CONFIG)

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
        self.producer.produce(CONFLUENT_TOPIC, key=b'0', value=data)
        self.producer.flush()
