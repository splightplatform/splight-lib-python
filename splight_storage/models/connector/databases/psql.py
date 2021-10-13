from splight_lib.connector import ConnectorInterface, ConnectorTypes


class PSQLDatabaseConnector(ConnectorInterface):
    type = ConnectorTypes.DATABASE

    def read(self):
        raise NotImplementedError