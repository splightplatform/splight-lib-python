from pandas import DataFrame
from pandas import json_normalize
from typing import Dict, List
from datetime import datetime

from splight_storage.models.asset.base_asset import BaseAsset
from splight_lib.tag import Tag
from splight_lib.component import DigitalOfferComponent
from splight_lib.tenant import Tenant
from splight_lib.communication import Variable


class FakeDatalakeClient:
    def __init__(self, database: str = 'default') -> None:
        pass

    @staticmethod
    def get_database_name_from_tenant(tenant: Tenant) -> str:
        return "default"

    @staticmethod
    def get_collection_from_component_and_tag(doc: DigitalOfferComponent, tag: Tag) -> str:
        return "_".join([doc.name, str(tag.id)])

    @staticmethod
    def get_filters_from_asset(asset: BaseAsset) -> Dict:
        return {}

    def find(self, collection: str, filters: Dict = None, **kwargs) -> List[Dict]:
        return [
            {
                "_id": "jashdasd",
                "asset_id": "1",
                "p": {
                    "value": 1
                },
                "timestamp": datetime.now()
            },
            {
                "_id": "jashdasd",
                "asset_id": "1",
                "p": {
                    "value": 4
                },
                "timestamp": datetime.now()
            }
        ]

    def find_dataframe(self, **kwargs) -> DataFrame:
        return json_normalize(list(self.find(**kwargs)))

    def delete_many(self, collection: str, filters: Dict = {}) -> None:
        pass

    def insert_many(self, collection: str, data: List[Dict], **kwargs) -> None:
        pass

    def insert_many_dataframe(self, collection: str, data: DataFrame, **kwargs) -> None:
        pass

    def aggregate(self, collection: str, pipeline: List[Dict]) -> List[Dict]:
        return {
            "_id": "jashdasd",
            "asset_id": "1",
            "p": {
                "value": 5
            },
            "timestamp": datetime.now()
        }

    def update_pipe(self, asset_ids: List[int], merge_fields: Dict) -> List[Dict]:
        return []

    def fetch_updates(self, variables: List[Variable]) -> List[Variable]:
        var = self.aggregate("", [])
        vars = []
        for v in variables:
            if v.field in var:
                v.args = var[v.field]
                vars.append(v)
        return vars

    def fetch_asset(self, asset: BaseAsset) -> None:
        pass

    def push_updates(self, variables: List[Variable]) -> None:
        pass
