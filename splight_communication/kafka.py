import logging
from typing import Dict
from confluent_kafka import Consumer, Producer
from confluent_kafka.admin import AdminClient, NewTopic
from .settings import CONFLUENT_CONSUMER_CONFIG, CONFLUENT_PRODUCER_CONFIG, CONFLUENT_ADMIN_CONFIG
from .abstract import AbstractCommunication


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

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

    @staticmethod
    def create_topic(topic: str) -> None:
        admin_client = AdminClient(CONFLUENT_ADMIN_CONFIG)
        result = admin_client.create_topics([NewTopic(topic, num_partitions=6, replication_factor=3)])

        # Wait for each operation to finish.
        for topic, f in result.items():
            try:
                f.result()  # The result itself is None
                print("Topic {} created".format(topic))
            except Exception as e:
                print("Failed to create topic {}: {}".format(topic, e))
