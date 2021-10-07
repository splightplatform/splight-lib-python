from enum import Enum
from abc import ABCMeta
from typing import FrozenSet

from splight_lib.connector import ConnectorInterface
from splight_lib.status import STATUS_UNKNOWN

class AssetType(Enum):
    UNKNOWN = 1
    DEVICE = 2


class Asset(metaclass=ABCMeta):
    type = AssetType.UNKNOWN

    def __init__(self, name, connector: ConnectorInterface) -> None:
        self.name = name
        self.connector = connector
        self.status = STATUS_UNKNOWN


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

    def get_assets(self) -> FrozenSet[Asset]:
        return self._assets
