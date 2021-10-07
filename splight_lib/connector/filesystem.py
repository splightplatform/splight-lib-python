import os
import pandas as pd
from typing import Callable
from functools import reduce
from splight_lib.connector import ConnectorInterface, ConnectorTypes


class FTPConnector(ConnectorInterface):
    type = ConnectorTypes.FILESYSTEM

    def read(self):
        raise NotImplementedError


class LocalFSConnector(ConnectorInterface):
    type = ConnectorTypes.FILESYSTEM

    def __init__(self, path, filter_: Callable) -> None:
        self.path = path
        self.filter_ = filter_

    @staticmethod
    def _list_files(cwd):
        return [
            os.path.join(cwd, f)
            for f in os.listdir(cwd)
            if os.path.isfile(os.path.join(cwd, f))
        ]

    def _read_file(self, **kwargs):
        # TODO select right reader depending on the extension
        # read_xlsx, read_csv, etc
        df = pd.read_csv(self.path, **kwargs)
        return df[self.filter_]
    
    def read(self, **kwargs):
        if os.path.isfile(self.path):
            return self._read_file(**kwargs)
        dfs = [self._read_file(f) for f in self._list_files(self.path)]
        df_merged = reduce(
            lambda  left,right: 
            pd.merge(left, right, how='outer'), dfs
        )
        return df_merged
