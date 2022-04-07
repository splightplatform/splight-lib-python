from datetime import datetime
from unittest import TestCase
from unittest.mock import patch, call
from pymongo.database import Database
from splight_communication import Variable
from splight_datalake.mongo import MongoClient


class TestMongoClient(TestCase):
    def test_init_with_args(self):
        client = MongoClient("database_name")
        self.assertIsInstance(client.db, Database)
        self.assertEqual(client.db.name, "databasename")

    def test_init_with_defaults(self):
        client = MongoClient()
        self.assertIsInstance(client.db, Database)
        self.assertEqual(client.db.name, "default")

    def test_get_variable(self):
        vars = [
            Variable(asset_id="1", attribute_id="1", args={"value": "value1"}, timestamp=datetime(2012, 1, 1, 8, 0))
        ]
        return_value = [
            {
                "asset_id": "1",
                "attribute_id": "1",
                "args": {"value": "value2"},
                "timestamp": datetime(2012, 1, 1, 8, 0)
            }
        ]
        expected_result = [
            Variable(asset_id="1", attribute_id="1", args={"value": "value2"}, path=None, timestamp=datetime(2012, 1, 1, 8, 0))
        ]
        client = MongoClient()
        with patch("splight_datalake.mongo.MongoClient._find", return_value=return_value) as find_call:
            self.assertEqual(client.get(Variable, asset_id="1", attribute_id="1"), expected_result)
            find_call.assert_called_once_with(
                collection='default',
                filters={
                    "asset_id": "1",
                    "attribute_id": "1"
                },
                limit=50,
                skip=0,
                sort=[('timestamp', -1)]
            )

    def test_get_multiple_variables(self):
        vars = [
            Variable(asset_id="1", attribute_id="1", args={}),
            Variable(asset_id="2", attribute_id="2", args={})
        ]
        first_call = [
            {
                "asset_id": "1",
                "attribute_id": "1",
                "args": {"value": "value1"},
                "timestamp": datetime(2012, 1, 1, 17, 0)
            },
            {
                "asset_id": "1",
                "attribute_id": "1",
                "args": {"value": "value2"},
                "timestamp": datetime(2012, 1, 1, 17, 1)
            },
            {
                "asset_id": "1",
                "attribute_id": "1",
                "args": {"value": "value3"},
                "timestamp": datetime(2012, 1, 1, 17, 2)
            },
        ]

        second_call = [
            {
                "asset_id": "2",
                "attribute_id": "2",
                "args": {"value": "value1"},
                "timestamp": datetime(2012, 1, 1, 17, 0)
            },
            {
                "asset_id": "2",
                "attribute_id": "2",
                "args": {"value": "value2"},
                "timestamp": datetime(2012, 1, 1, 17, 1)
            },
            {
                "asset_id": "2",
                "attribute_id": "2",
                "args": {"value": "value3"},
                "timestamp": datetime(2012, 1, 1, 17, 2)
            }
        ]
        expected_result_first_call = [
            Variable(asset_id="1", attribute_id="1", args={"value": "value1"}, path=None, timestamp=datetime(2012, 1, 1, 17, 0)),
            Variable(asset_id="1", attribute_id="1", args={"value": "value2"}, path=None, timestamp=datetime(2012, 1, 1, 17, 1)),
            Variable(asset_id="1", attribute_id="1", args={"value": "value3"}, path=None, timestamp=datetime(2012, 1, 1, 17, 2))
        ]
        expected_result_second_call = [
            Variable(asset_id="2", attribute_id="2", args={"value": "value1"}, path=None, timestamp=datetime(2012, 1, 1, 17, 0)),
            Variable(asset_id="2", attribute_id="2", args={"value": "value2"}, path=None, timestamp=datetime(2012, 1, 1, 17, 1)),
            Variable(asset_id="2", attribute_id="2", args={"value": "value3"}, path=None, timestamp=datetime(2012, 1, 1, 17, 2))
        ]

        client = MongoClient()
        with patch("splight_datalake.mongo.MongoClient._find", side_effect=[first_call, second_call]) as find_call:
            self.assertEqual(client.get(resource_type=Variable, asset_id="1", attribute_id="1", limit_=3, from_=datetime(2012, 1, 1, 17, 0), to_=datetime(2012, 1, 1, 18, 0)), expected_result_first_call)
            self.assertEqual(client.get(resource_type=Variable, asset_id__in=["2"], attribute_id__contains="2", limit_=3, from_=datetime(2012, 1, 1, 17, 0), to_=datetime(2012, 1, 1, 18, 0)), expected_result_second_call)
            find_call.assert_has_calls([
                call(
                    collection='default',
                    filters={
                        "asset_id": "1",
                        "attribute_id": "1",
                        "timestamp": {
                            "$gte": datetime(2012, 1, 1, 17, 0),
                            "$lte": datetime(2012, 1, 1, 18, 0)
                        }
                    },
                    limit=3,
                    skip=0,
                    sort=[('timestamp', -1)]),
                call(
                    collection='default',
                    filters={
                        "asset_id": {"$in": ["2"]},
                        "attribute_id": {"$regex": "2"},
                        "timestamp": {
                            "$gte": datetime(2012, 1, 1, 17, 0),
                            "$lte": datetime(2012, 1, 1, 18, 0)
                        }
                    },
                    limit=3,
                    skip=0,
                    sort=[('timestamp', -1)])
            ])

    def test_save_variable(self):
        vars = [
            Variable(asset_id="1", attribute_id="1", args={"value": "value1"}, timestamp=datetime(2012, 1, 1, 8, 0)),
            Variable(asset_id="2", attribute_id="1", args={"value": "value1"}, timestamp=datetime(2012, 1, 1, 8, 0)),
            Variable(asset_id="2", attribute_id="2", args={"value": "value2"}, timestamp=datetime(2012, 1, 1, 8, 0)),
        ]
        expected_data_list = [
            {
                "args": {"value": "value1"},
                "path": None,
                "asset_id": "1",
                "attribute_id": "1",
                "timestamp": datetime(2012, 1, 1, 8, 0)
            },
            {
                "args": {"value": "value1"},
                "path": None,
                "asset_id": "2",
                "attribute_id": "1",
                "timestamp": datetime(2012, 1, 1, 8, 0)
            },
            {
                "args": {"value": "value2"},
                "path": None,
                "asset_id": "2",
                "attribute_id": "2",
                "timestamp": datetime(2012, 1, 1, 8, 0)
            },
        ]
        client = MongoClient()
        with patch("splight_datalake.mongo.MongoClient._insert_many", return_value=None) as ins_call:
            client.save(resource_type=Variable, instances=vars)
            ins_call.assert_called_once_with('default', data=expected_data_list)

    def test_filter_in_dict(self):
        return_value = [
            {
                "asset_id": "1",
                "attribute_id": "1",
                "args": {"value": "value1"},
                "timestamp": datetime(2012, 1, 1, 8, 0)
            }
        ]
        expected_result = [
            Variable(asset_id="1", attribute_id="1", args={"value": "value1"}, timestamp=datetime(2012, 1, 1, 8, 0))
        ]
        client = MongoClient()
        with patch("splight_datalake.mongo.MongoClient._find", return_value=return_value) as find_call:
            self.assertEqual(client.get(Variable, args__value="value1"), expected_result)
            find_call.assert_called_once_with(
                collection='default',
                filters={
                    "args.value": "value1"
                },
                limit=50,
                skip=0,
                sort=[('timestamp', -1)]
            )
