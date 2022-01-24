from unittest import TestCase
from unittest.mock import patch
from pymongo.database import Database
# TODO https://splight.atlassian.net/browse/FAC-223 Fix circular reference.
from django.utils import timezone
from parameterized import parameterized
from splight_datalake.database.mongo import MongoPipelines, MongoClient
from splight_communication import Variable


class FakeDate(timezone.datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2021, 5, 12)


class TestMongoPipelines(TestCase):
    @parameterized.expand([
        ([],),
        ([1, 2, 3],),
    ])
    @patch('splight_datalake.database.mongo.timezone.datetime', new=FakeDate)
    def test_fetch_assets(self, asset_id_list):
        min_date = FakeDate.now() - timezone.timedelta(minutes=10)
        self.assertEqual(len(MongoPipelines.fetch_assets(asset_id_list)), 5)
        self.assertEqual(MongoPipelines.fetch_assets(asset_id_list)[0], {'$match': {'asset_id': {'$in': asset_id_list}, 'timestamp': {'$gte': {'$date': str(min_date)}}}}),
        self.assertEqual(MongoPipelines.fetch_assets(asset_id_list)[1], {'$sort': {'timestamp': 1}})
        self.assertEqual(MongoPipelines.fetch_assets(asset_id_list)[2], {'$group': {'_id': {'asset_id': '$asset_id'}, 'item': {'$mergeObjects': '$$ROOT'}}})
        self.assertEqual(MongoPipelines.fetch_assets(asset_id_list)[3], {'$replaceRoot': {'newRoot': '$item'}})
        self.assertEqual(MongoPipelines.fetch_assets(asset_id_list)[4], {'$project': {'_id': 0, 'timestamp': 0}})


class TestMongoClient(TestCase):
    def test_init_with_args(self):
        client = MongoClient("database_name")
        self.assertIsInstance(client.db, Database)
        self.assertEqual(client.db.name, "database_name")

    def test_init_with_defaults(self):
        client = MongoClient()
        self.assertIsInstance(client.db, Database)
        self.assertEqual(client.db.name, "default")

    def test_find(self):
        client = MongoClient()
        return_value = [1, 2, 3]
        filters = {}
        with patch("pymongo.collection.Collection.find", return_value=return_value) as find_call:
            self.assertEqual(client.find(collection="a_coll", filters=filters), return_value)
            find_call.assert_called_once_with(filter=filters, return_key=False)

    def test_aggregate(self):
        client = MongoClient()
        return_value = [1, 2, 3]
        pipeline = [{}, {}, {}]
        with patch("pymongo.collection.Collection.aggregate", return_value=return_value) as agg_call:
            self.assertEqual(client.aggregate(collection="a_coll", pipeline=pipeline), return_value)
            agg_call.assert_called_once_with(pipeline)

    def test_delete_many(self):
        client = MongoClient()
        filters = {}
        with patch("pymongo.collection.Collection.delete_many", return_value=None) as del_call:
            self.assertIsNone(client.delete_many(collection="a_coll", filters=filters))
            del_call.assert_called_once_with(filters)

    def test_insert_many(self):
        client = MongoClient()
        data = []
        kwarg1 = "kwarg1"
        with patch("pymongo.collection.Collection.insert_many", return_value=None) as ins_call:
            self.assertIsNone(client.insert_many(collection="a_coll", data=data, kwarg1=kwarg1))
            ins_call.assert_called_once_with(data, kwarg1=kwarg1)

    @patch('splight_datalake.database.mongo.timezone.datetime', new=FakeDate)
    def test_fetch_updates(self):
        vars = [
            Variable(asset_id=1, field="field1", args={}),
            Variable(asset_id=2, field="field1", args={}),
            Variable(asset_id=2, field="field2", args={}),
        ]
        return_value = [
            {
                "asset_id": 1,
                "field1": {"value": "value1"}
            },
            {
                "asset_id": 2,
                "field1": {"value": "value1"},
                "field2": {"value": "value2"}
            },
        ]
        expected_result = [
            Variable(asset_id=1, field="field1", args={"value": "value1"}, path=None),
            Variable(asset_id=2, field="field1", args={"value": "value1"}, path=None),
            Variable(asset_id=2, field="field2", args={"value": "value2"}, path=None),
        ]
        client = MongoClient()
        with patch("splight_datalake.database.mongo.MongoClient.aggregate", return_value=return_value) as agg_call:
            self.assertEqual(client.fetch_updates(variables=vars), expected_result)
            agg_call.assert_called_once_with(client.UPDATES_COLLECTION, MongoPipelines.fetch_assets([1, 2]))

    @patch('splight_datalake.database.mongo.timezone.datetime', new=FakeDate)
    def test_push_updates(self):
        vars = [
            Variable(asset_id=1, field="field1", args={"value": "value1"}),
            Variable(asset_id=2, field="field1", args={"value": "value1"}),
            Variable(asset_id=2, field="field2", args={"value": "value2"}),
        ]
        expected_data_list = [
            {
                "asset_id": '1',
                "field1": {"value": "value1"},
                "timestamp": FakeDate.now()
            },
            {
                "asset_id": '2',
                "field1": {"value": "value1"},
                "timestamp": FakeDate.now()
            },
            {
                "asset_id": '2',
                "field2": {"value": "value2"},
                "timestamp": FakeDate.now()
            },
        ]
        client = MongoClient()
        with patch("splight_datalake.database.mongo.MongoClient.insert_many", return_value=None) as ins_call:
            client.push_updates(variables=vars)
            ins_call.assert_called_once_with(client.UPDATES_COLLECTION, data=expected_data_list)
