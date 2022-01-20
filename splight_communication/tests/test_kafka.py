from unittest import TestCase
from unittest.mock import patch
from collections import defaultdict
from splight_communication.kafka import KafkaQueueCommunication


class FakeMessage:
    def __init__(self, value=b'{}', error=False) -> None:
        self._error = error
        self._value = value

    def error(self):
        return self._error

    def value(self):
        return self._value

class FakeConsumer:
    def __init__(self, messages=[FakeMessage()]):
        self._messages = messages

    def consume(self, *args, **kwargs):
        return [self._messages.pop()]


class FakeProducer:
    def __init__(self):
        self.messages = defaultdict(list)
        self.flushed = False

    def produce(self, topic, value, *args, **kwargs):
        self.messages[topic].append(value)

    def flush(self):
        self.flushed = True


class TestKafkaClient(TestCase):
    def test_init_with_args(self):
        client = KafkaQueueCommunication("topic1")
        self.assertEqual(client.topic, "topic1")
        
    def test_init_with_defaults(self):
        client = KafkaQueueCommunication()
        self.assertEqual(client.topic, "default")

    def test_client_recv(self):
        client = KafkaQueueCommunication("topic1")
        expected_message = {'key': 'value'}
        client.consumer = FakeConsumer(messages=[FakeMessage(value=client._encode(expected_message))])
        message = client.receive()
        self.assertEqual(message, expected_message)
    
    def test_client_recv_dismiss_error_message(self):
        expected_message = {'key': 'value'}
        client = KafkaQueueCommunication("topic1")
        client.consumer = FakeConsumer(messages=[
            FakeMessage(error=True),
            FakeMessage(value=client._encode(expected_message))
        ])
        message = client.receive()
        self.assertEqual(message, expected_message)

    def test_client_send(self):
        expected_message = {'key': 'value'}
        topic = "topic1"
        client = KafkaQueueCommunication(topic)
        client.producer = FakeProducer()
        client.send(data=expected_message)
        self.assertTrue(client.producer.flushed)
        message = client.producer.messages[topic].pop()
        self.assertEqual(client._decode(message),expected_message)
