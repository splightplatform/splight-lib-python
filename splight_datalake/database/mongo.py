import logging
from pymongo import MongoClient as PyMongoClient
from pandas import DataFrame
from pandas import json_normalize
from typing import Dict, List
from django.utils import timezone
from splight_storage.models.asset.base_asset import BaseAsset
from splight_lib.tag import Tag
from splight_lib.component import DigitalOfferComponent
from splight_lib.tenant import Tenant
from splight_lib.communication import Variable
from splight_datalake.settings import setup


class MongoPipelines:

    @staticmethod
    def fetch_assets(asset_ids: List[int]) -> List[Dict]:

        min_date = timezone.datetime.now() - timezone.timedelta(minutes=10)

        pipe = [
            {'$match':
                {
                    'asset_id': {'$in': asset_ids},
                    'timestamp': {'$gte': {'$date': str(min_date)}}
                }
             },
            {"$sort":
                {
                    "timestamp": 1
                }
             },
            {'$group':
                {
                    '_id': {'asset_id': '$asset_id'},
                    'item': {'$mergeObjects': '$$ROOT'},
                }
             },
            {'$replaceRoot':
                {
                    'newRoot': '$item'
                }
             },
            {"$project":
                {
                    "_id": 0,
                    "timestamp": 0
                }
             }
        ]
        return pipe


class MongoClient:
    logger = logging.getLogger()
    REPORTS_COLLECTION = "reports"
    UPDATES_COLLECTION = "updates"

    def __init__(self, database: str = 'default') -> None:
        connection = f'{setup["PROTOCOL"]}://{setup["USER"]}:{setup["PASSWORD"]}@{setup["HOST"]}'
        if setup["PORT"]:
            connection = f'{connection}:{setup["PORT"]}'
        client = PyMongoClient(connection)
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

    def aggregate(self, collection: str, pipeline: List[Dict]) -> List[Dict]:
        documents = self.db[collection].aggregate(pipeline)
        return documents

    def delete_many(self, collection: str, filters: Dict = {}) -> None:
        self.db[collection].delete_many(filters)

    def insert_many(self, collection: str, data: List[Dict], **kwargs) -> None:
        self.db[collection].insert_many(data, **kwargs)

    def fetch_updates(self, variables: List[Variable]) -> List[Variable]:
        if len(variables) < 1:
            return []

        asset_ids = list(set([int(v.asset_id) for v in variables]))

        variables = []
        for update in self.aggregate(self.UPDATES_COLLECTION, MongoPipelines.fetch_assets(asset_ids)):
            asset_id = update['asset_id']
            for field, args in update.items():
                if field != 'asset_id':
                    var: Variable = Variable(asset_id=asset_id, field=field, args=args)
                    variables.append(var)
        return variables

    def push_updates(self, variables: List[Variable]) -> None:
        if len(variables) < 1:
            return
        data_list = []
        for var in variables:
            data = dict()
            data['asset_id'] = var.asset_id
            data[var.field] = var.args
            data['timestamp'] = timezone.datetime.now()
            data_list.append(data)
        self.insert_many(self.UPDATES_COLLECTION, data=data_list)

    def fetch_asset(self, asset: BaseAsset) -> None:
        raise NotImplementedError

    def push_asset(self, asset: BaseAsset) -> None:
        raise NotImplementedError

    def find_dataframe(self, **kwargs) -> DataFrame:
        return json_normalize(list(self.find(**kwargs)))

    def insert_many_dataframe(self, collection: str, data: DataFrame, **kwargs) -> None:
        kwargs.update(collection=collection)
        kwargs.update(data=data.to_dict("records"))
        self.insert_many(**kwargs)
