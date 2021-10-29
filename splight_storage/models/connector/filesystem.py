import os
import pandas as pd
from django.db import models
from typing import List
from functools import reduce
from pandas.core.frame import DataFrame
from . import ConnectorInterface


class FTPConnector(ConnectorInterface):
    ftp_connection_string = models.CharField(max_length=200, null=True)

    def read(self):
        raise NotImplementedError


class LocalFSConnector(ConnectorInterface):
    path = models.FilePathField(max_length=10, null=True, blank=True)
    query = models.CharField(max_length=100, default=None, null=True)
    sort_by = models.CharField(max_length=100, default=None, null=True)

    @staticmethod
    def _list_files(cwd):
        return [
            os.path.join(cwd, f)
            for f in os.listdir(cwd)
            if os.path.isfile(os.path.join(cwd, f))
        ]

    def _apply_filter(self, df) -> DataFrame:
        if self.query is None:
            return df
        return df.query(self.query)

    def _apply_sort(self, df) -> DataFrame:
        if not self.sort_by:
            return df
        return df.sort_values(self.sort_by)

    def _read_files_from_dir(self, **kwargs):
        dfs = [self._read_file(f, **kwargs)
               for f in self._list_files(self.path)]
        df = reduce(
            lambda left, right:
            pd.merge(left, right, how='outer'), dfs
        )
        return df

    def _read_file(self, **kwargs):
        # TODO select right reader depending on the extension
        # read_xlsx, read_csv, etc
        df = pd.read_csv(self.path, **kwargs)
        df = self._apply_filter(df)
        return df

    def hist(self, **kwargs) -> DataFrame:
        if os.path.isfile(self.path):
            func = self._read_file
        else:
            func = self._read_files_from_dir
        df = func(**kwargs)
        df = self._apply_sort(df)
        return df

    def read(self, **kwargs) -> DataFrame:
        df = self.hist()
        return df.tail(1)
