from splight_lib.communication import AbstractCommunication


class FakeQueueCommunications(AbstractCommunication):
    def send(self, data: dict):
        pass

    def receive(self) -> dict:
        return {'data': 'test'}
