from enum import Enum
from abc import ABCMeta

from splight_lib.connector import ConnectorInterface

class AssetType(Enum):
    UNKNOWN = 1
    DEVICE = 2

    @classmethod
    def __all__(cls):
        return [c.value for c in cls]


class Asset(metclass=ABCMeta):
    type = AssetType.UNKNOWN

    def __init__(self, name, connector: ConnectorInterface) -> None:
        self.name = name
        self.connector = connector


class RelayAsset(Asset):
    type = AssetType.DEVICE


class Network:
    def __init__(self, name) -> None:
        self.name = name
        self.clear()
    
    def add_asset(self, asset: Asset) -> None:
        self._assets.add(asset)
    
    def del_asset(self, asset: Asset) -> None:
        self._assets.remove(asset)

    def clear(self) -> None:
        self._assets = set()
