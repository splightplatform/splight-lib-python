import logging
from pymongo import MongoClient as PyMongoClient, DESCENDING
from pandas import DataFrame
from pandas import json_normalize
from typing import Dict, List
from datetime import datetime
from splight_storage.models.asset.base_asset import BaseAsset
from splight_lib.tag import Tag
from splight_lib.component import DigitalOfferComponent
from splight_lib.tenant import Tenant
from splight_lib.communication import Variable
from splight_datalake.settings import setup


class MongoClient:
    logger = logging.getLogger()
    REPORTS_COLLECTION = "reports"
    UPDATES_COLLECTION = "updates"

    def __init__(self, database: str = 'default') -> None:
        connnection = f'{setup["PROTOCOL"]}://{setup["USER"]}:{setup["PASSWORD"]}@{setup["HOST"]}:{setup["PORT"]}'
        client = PyMongoClient(connnection)
        self.db = client[database]

    @staticmethod
    def get_database_name_from_tenant(tenant: Tenant) -> str:
        return tenant.org_id

    @staticmethod
    def get_collection_from_component_and_tag(doc: DigitalOfferComponent, tag: Tag) -> str:
        return "_".join([doc.name, str(tag.id)])

    @staticmethod
    def get_filters_from_asset(asset: BaseAsset) -> Dict:
        filters = {}
        filters["asset_id"] = asset.id
        filters["asset_external_id"] = asset.external_id
        return filters

    def find(self, collection: str, filters: Dict = None, **kwargs) -> List[Dict]:
        documents = self.db[collection].find(
            filter=filters,
            return_key=False,
            **kwargs
        )
        return documents

    def find_dataframe(self, **kwargs) -> DataFrame:
        return json_normalize(list(self.find(**kwargs)))

    def delete_many(self, collection: str, filters: Dict = {}) -> None:
        self.db[collection].delete_many(filters)

    def insert_many(self, collection: str, data: List[Dict], **kwargs) -> None:
        self.db[collection].insert_many(data, **kwargs)

    def insert_many_dataframe(self, collection: str, data: DataFrame, **kwargs) -> None:
        kwargs.update(collection=collection)
        kwargs.update(data=data.to_dict("records"))
        self.insert_many(**kwargs)

    def aggregate(self, collection: str, pipeline: List[Dict]) -> List[Dict]:
        documents = self.db[collection].aggregate(pipeline)
        return documents

    def update_pipe(self, asset_ids: List[int], merge_fields: Dict) -> List[Dict]:
        pipe = [
            {
                '$match': {
                    'asset_id': {'$in': asset_ids}
                }
            },
            {
                '$group': {
                    '_id': {
                        'asset_id': '$asset_id',
                        'timestamp': '$timestamp'
                    },
                    'fields': {
                        '$mergeObjects': merge_fields
                    }
                }
            },
            {
                '$sort': {'_id.timestamp': -1}
            },
            {
                '$limit': max(len(asset_ids), 1)
            }
        ]

        return pipe

    def fetch_updates(self, variables: List[Variable]) -> List[Variable]:
        asset_ids = list(set([int(v.asset_id) for v in variables]))

        merge_fields = {
            v.field: '$' + v.field for v in variables
        }

        pipe = self.update_pipe(asset_ids, merge_fields)
        updates = self.aggregate(self.UPDATES_COLLECTION, pipe)
        variables = []

        for update in updates:
            asset_id = update['_id']['asset_id']
            for field, args in update['fields'].items():
                var: Variable = Variable(asset_id=asset_id, field=field, args=args)
                variables.append(var)
        return variables

    def fetch_asset(self, asset: BaseAsset) -> None:
        data = self.find(self.UPDATES_COLLECTION, filters={'asset_id': asset.id}, sort=[('timestamp', DESCENDING)], limit=1)[0]
        for key, value in data['args'].items():
            setattr(asset, key, value)

    def push_updates(self, variables: List[Variable]) -> None:
        if len(variables) < 1:
            return
        data_list = []
        for var in variables:
            data = dict()
            data['asset_id'] = var.asset_id
            data[var.field] = var.args
            data['timestamp'] = datetime.now()
            data_list.append(data)
        self.insert_many(self.UPDATES_COLLECTION, data=data_list)
