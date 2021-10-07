from abc import ABCMeta, abstractmethod
from enum import Enum, Boolean
from typing import List

from splight_lib.asset import  Network, Asset, AssetType


class ComponentType(Enum):
    UNKNOWN = 1
    DATA_INGESTOR = 2  # Only for data store
    ORACLE = 3         # Predictions for the future
    GUIDE = 4          # Alerting and recomendations
    ACTOR = 5          # Active manager for the infrastructure


class DOComponentInterface(metaclass=ABCMeta):
    type = ComponentType.UNKNOWN
    _asset_applicable = AssetType.__all__

    def is_applicable(self, asset: Asset) -> Boolean:
        return asset.type in self._asset_applicable

    @abstractmethod
    def execute(self, network: Network):
        pass


class DigitalOffer:
    def __init__(self, components: List[DOComponentInterface], network: Network) -> None:
        self.components = components

    def execute(self, network: Network):
        raise NotImplementedError
