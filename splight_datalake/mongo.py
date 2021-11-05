import logging
from pymongo import MongoClient
from pandas import DataFrame
from pandas.io.json import json_normalize
from splight_lib.asset import Asset
from typing import Dict, List
from splight_datalake.settings import setup


class DatalakeClient:
    logger = logging.getLogger()

    def __init__(self, database: str = 'default') -> None:
        connnection = f'mongodb://{setup["USER"]}:{setup["PASSWORD"]}@{setup["HOST"]}:{setup["PORT"]}'
        client = MongoClient(connnection)
        self.db = getattr(client, database)

    def find(self, asset: Asset, collection: str, filters_: Dict = {}) -> DataFrame:
        if 'asset_id' in filters_.keys() or "asset_external_id" in filters_.keys():
            self.logger.warning("asset_id and asset_external_id going to be overwritten")
        filters_["asset_id"] = asset.id
        filters_["asset_external_id"] = asset.external_id
        documents = getattr(self.db, collection).find(filters_)
        return json_normalize(list(documents))

    def delete_many(self, asset: Asset, collection: str, filters_: Dict = {}) -> None:
        if 'asset_id' in filters_.keys() or "asset_external_id" in filters_.keys():
            self.logger.warning("asset_id and asset_external_id going to be overwritten")
        filters_["asset_id"] = asset.id
        filters_["asset_external_id"] = asset.external_id
        getattr(self.db, collection).delete_many(filters_)

    def insert_many(self, asset: Asset, data: DataFrame, collection: str) -> None:
        if 'asset_id' in data.columns or "asset_external_id" in data.columns:
            self.logger.warning("asset_id and asset_external_id going to be overwritten")
        data["asset_id"] = asset.id
        data["asset_external_id"] = asset.external_id
        getattr(self.db, collection).insert_many(data.to_dict("records"))

    def insert_or_update_many(self, asset: Asset, data: DataFrame, collection: str, indexes: List[str] = []) -> None:
        if 'asset_id' in data.columns or "asset_external_id" in data.columns:
            self.logger.warning("asset_id and asset_external_id going to be overwritten")
        indexes += ["asset_id", "asset_external_id"]
        data["asset_id"] = asset.id
        data["asset_external_id"] = asset.external_id
        for _, row in data.iterrows():
            # Update try
            result = getattr(self.db, collection).find_one_and_update(
                {key: row[key] for key in indexes}, 
                {"$set": row.to_dict()}
            )
            # Insert if not updated
            if result is None:
                getattr(self.db, collection).insert(row.to_dict())