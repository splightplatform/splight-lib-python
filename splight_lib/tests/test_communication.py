from unittest import TestCase


class TestCommunication(TestCase):
    def test_import_communication(self):
        from splight_lib.communication import InternalCommunicationClient, ExternalCommunicationClient