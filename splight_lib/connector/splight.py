from splight_lib.connector import ConnectorTypes, ConnectorInterface


class SplightBoxConnector(ConnectorInterface):
    type = ConnectorTypes.SPLIGHT

    def read(self):
        raise NotImplementedError