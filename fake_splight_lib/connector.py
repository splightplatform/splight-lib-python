from mock import Mock
from splight_lib.connector import ConnectorInterface, ConnectorTypes


class FakeConnector(ConnectorInterface):
    type = ConnectorTypes.FAKE

    def read(self):
        return Mock()