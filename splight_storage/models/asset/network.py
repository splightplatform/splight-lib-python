from typing import FrozenSet
from . import Asset


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
