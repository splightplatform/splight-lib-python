from enum import Enum
from typing import FrozenSet
from django.db import models
from pandas.core.frame import DataFrame
from typedmodels.models import TypedModel

from ..connector import ConnectorInterface


class Asset(TypedModel):
    name = models.CharField(max_length=100)
    connector = models.ForeignKey(ConnectorInterface, on_delete=models.CASCADE)
    
    class Meta:
        app_label = 'splight_storage'

    def read(self) -> DataFrame:
        if not self.connector:
            raise NotImplementedError
        return self.connector.read()

    def hist(self, from_datalake: bool = False) -> DataFrame:
        if from_datalake:
            raise NotImplementedError
        if not self.connector:
            raise NotImplementedError
        return self.connector.hist()
