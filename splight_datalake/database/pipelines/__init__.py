from .fetch_assets import get_fetch_assets_pipeline
from .asset_history import get_asset_history_pipeline
from .digital_offer_component_history import get_digital_offer_component_pipeline
from splight_storage.models.asset.base_asset import BaseAsset
from datetime import datetime
from typing import List, Dict, Optional


class MongoPipelines:
    @staticmethod
    def fetch_assets(asset_ids: List[int]) -> List[Dict]:
        return get_fetch_assets_pipeline(asset_ids)

    @staticmethod
    def asset_history(asset: BaseAsset,
                      attributes: Optional[List[str]] = None,
                      from_: Optional[datetime] = None,
                      to_: Optional[datetime] = None) -> List[Dict]:
        return get_asset_history_pipeline(asset, attributes, from_, to_)

    @staticmethod
    def digital_offers_commponent_history(from_: Optional[datetime] = None,
                                          to_: Optional[datetime] = None) -> List[Dict]:
        return get_digital_offer_component_pipeline(from_, to_)
