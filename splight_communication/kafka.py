import logging
from typing import Dict
from confluent_kafka import Consumer, Producer
from .settings import CONFLUENT_CONSUMER_CONFIG, CONFLUENT_PRODUCER_CONFIG
from .abstract import AbstractCommunication


logger = logging.getLogger()


class KafkaQueueCommunication(AbstractCommunication):
    def __init__(self, *args, **kwargs):
        super(KafkaQueueCommunication, self).__init__(*args, **kwargs)
        self.topic = self.namespace
        self.consumer = Consumer(CONFLUENT_CONSUMER_CONFIG)
        self.consumer.subscribe([self.topic])
        self.producer = Producer(CONFLUENT_PRODUCER_CONFIG)

    def receive(self):
        msg = self.consumer.consume(num_messages=1, timeout=-1)[0]
        if msg.error():
            logger.error(f"Msg with error {msg.value()}")
            return self.receive()
        data = msg.value()
        return self._decode(data)

    def send(self, data: Dict) -> None:
        self.producer.produce(self.topic, value=self._encode(data))
        self.producer.flush()
