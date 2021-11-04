import logging
from pymongo import MongoClient
from pandas import DataFrame
from pandas.io.json import json_normalize
from splight_lib.asset import Asset
from typing import Dict
from splight_datalake import settings


class DatalakeClient:
    logger = logging.getLogger()

    def __init__(self, database: str = 'default') -> None:
        setup = settings.DATABASES[database]
        connnection = f'mongodb://{setup["USER"]}:{setup["PASSWORD"]}@{setup["HOST"]}:{setup["PORT"]}'
        client = MongoClient(connnection)
        self.db = getattr(client, database)

    def insert_many(self, asset: Asset, data: DataFrame, collection: str) -> None:
        if 'asset_id' in data.columns or "asset_external_id" in data.columns:
            self.logger.warning("asset_id and asset_external_id going to be overwritten")
        data["asset_id"] = asset.id
        data["asset_external_id"] = asset.external_id
        getattr(self.db, collection).insert_many(data.to_dict("records"))

    def find(self, asset: Asset, collection: str, filters_: Dict = {}) -> DataFrame:
        if 'asset_id' in filters_.keys() or "asset_external_id" in filters_.keys():
            self.logger.warning("asset_id and asset_external_id going to be overwritten")
        filters_["asset_id"] = asset.id
        filters_["asset_external_id"] = asset.external_id
        documents = getattr(self.db, collection).find(filters_)
        return json_normalize(list(documents))
