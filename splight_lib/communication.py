import os
from splight_communication import *
from fake_splight_lib.communication import FakeQueueCommunication

InternalCommunicationClient = ZMQueueCommunication

SELECTOR = {
    'zmq': ZMQueueCommunication,
    'kafka': KafkaQueueCommunication,
    'fake': FakeQueueCommunication,
}

ExternalCommunicationClient = SELECTOR.get(os.environ.get('COMMUNICATION', 'fake'))

__all__ = [
    "InternalCommunicationClient",
    "ExternalCommunicationClient",
    "Variable",
    "Message",
    "Action"
]
