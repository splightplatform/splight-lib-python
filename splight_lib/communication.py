import os
import ast
from splight_communication import ZMQueueCommunication, KafkaQueueCommunication, Variable, Message
from fake_splight_lib.communication import FakeQueueCommunication


InternalCommunicationClient = ZMQueueCommunication
ExternalCommunicationClient = KafkaQueueCommunication


if ast.literal_eval(os.getenv("FAKE_COMMUNICATION", "True")):
    InternalCommunicationClient = FakeQueueCommunication
    ExternalCommunicationClient = FakeQueueCommunication
