import logging
from pymongo import MongoClient
from pandas import DataFrame
from pandas.io.json import json_normalize
from build.lib.splight_storage.models.component import DigitalOfferComponent
from splight_lib.asset import Asset
from splight_lib.tag import Tag
from splight_lib.component import DigitalOfferComponent
from splight_lib.tenant import Tenant
from typing import Dict, List
from splight_datalake.settings import setup


class DatalakeClient:
    logger = logging.getLogger()
    REPORTS_COLLECTION = "reports"

    def __init__(self, database: str = 'default') -> None:
        connnection = f'{setup["PROTOCOL"]}://{setup["USER"]}:{setup["PASSWORD"]}@{setup["HOST"]}{setup["PORT"]}'
        client = MongoClient(connnection)
        self.db = client[database]

    @staticmethod
    def get_database_name_from_tenant(tenant: Tenant) -> str:
        return tenant.org_id

    @staticmethod
    def get_collection_from_component_and_tag(doc: DigitalOfferComponent, tag: Tag) -> str:
        return "_".join(doc.__class__.__name__, tag.id)

    @staticmethod
    def get_filters_from_asset(asset: Asset) -> Dict:
        filters_ = {}
        filters_["asset_id"] = asset.id
        filters_["asset_external_id"] = asset.external_id
        return filters_

    def find(self, collection: str, filters_: Dict = None, **kwargs) -> List[Dict]:
        documents = self.db[collection].find(
            filter=filters_,
            *kwargs
        )
        return documents

    def find_dataframe(self, **kwargs) -> DataFrame:
        return json_normalize(list(self.find(**kwargs)))
   
    def delete_many(self, collection: str, filters_: Dict = {}) -> None:
        self.db[collection].delete_many(filters_)

    def insert_many(self, collection: str, data: List[Dict], **kwargs) -> None:
        self.db[collection].insert_many(data, **kwargs)

    def insert_many_dataframe(self, data: DataFrame, **kwargs) -> None:
        kwargs.update(data=data.to_dict("records"))
        self.insert_many(**kwargs)
