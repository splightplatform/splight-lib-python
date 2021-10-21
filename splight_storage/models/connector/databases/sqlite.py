import pandas as pd
from sqlite3 import connect
from connector import ConnectorTypes, ConnectorInterface


class SQLiteDatabaseConnector(ConnectorInterface):
    type = ConnectorTypes.DATABASE

    def __init__(self, fetch_query, connection_string=':memory:') -> None:
        self.db_connection = connect(connection_string)
        self.fetch_query = fetch_query

    def _get_connection(self):
        return self.db_connection

    def write(self, table_name, df: pd.DataFrame):
        connection = self._get_connection()
        df.to_sql(table_name, connection)

    def read(self, **kwargs) -> pd.DataFrame:
        connection = self._get_connection()
        return pd.read_sql(self.fetch_query, connection, **kwargs)
