from abc import ABCMeta, abstractmethod
from .kafka import KafkaQueueCommunication 
from .zmq import ZMQueueCommunication


__all__ = [
    ZMQueueCommunication,
    KafkaQueueCommunication,
]


InternalCommunicationClient = ZMQueueCommunication
ExternalCommunicationClient = KafkaQueueCommunication