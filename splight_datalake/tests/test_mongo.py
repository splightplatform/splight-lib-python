from datetime import datetime, timezone
from unittest import TestCase
from unittest.mock import patch, call
from pymongo.database import Database
from parameterized import parameterized
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
            Variable(asset_id="1", attribute_id="1", args={"value": "value1"}, timestamp=datetime(2012, 1, 1, 8, 0), instance_id="1", instance_type="testtype")
        ]
        return_value = [
            {
                "asset_id": "1",
                "attribute_id": "1",
                "args": {"value": "value2"},
                "timestamp": datetime(2012, 1, 1, 8, 0),
                "instance_id": "1",
                "instance_type": "testtype" 
            }
        ]
        expected_result = [
            Variable(asset_id="1", attribute_id="1", args={"value": "value2"}, path=None, timestamp=datetime(2012, 1, 1, 8, 0), instance_id="1", instance_type="testtype")
        ]
        client = MongoClient()
        pipeline = client._get_pipeline(
            filters={
                "asset_id": {"$eq": "1"},
                "attribute_id": {"$eq": "1"}
            },
            limit=50,
            skip=0,
            sort=[('timestamp', -1)],
            group_id=[],
            group_fields=[]
        )
        with patch("splight_datalake.mongo.MongoClient._aggregate", return_value=return_value) as find_call:
            self.assertEqual(client.get(Variable, asset_id="1", attribute_id="1"), expected_result)
            find_call.assert_called_once_with(
                collection='default',
                pipeline=pipeline,
                tzinfo=timezone.utc
            )

    def test_get_multiple_variables(self):
        vars = [
            Variable(asset_id="1", attribute_id="1", instance_id="1", instance_type="testtype", args={}),
            Variable(asset_id="2", attribute_id="2", instance_id="1", instance_type="testtype", args={})
        ]
        first_call = [
            {
                "asset_id": "1",
                "attribute_id": "1",
                "args": {"value": "value1"},
                "timestamp": datetime(2012, 1, 1, 17, 0),
                "instance_id": "1",
                "instance_type": "testtype"
            },
            {
                "asset_id": "1",
                "attribute_id": "1",
                "args": {"value": "value2"},
                "timestamp": datetime(2012, 1, 1, 17, 1),
                "instance_id": "1",
                "instance_type": "testtype" 
            },
            {
                "asset_id": "1",
                "attribute_id": "1",
                "args": {"value": "value3"},
                "timestamp": datetime(2012, 1, 1, 17, 2),
                "instance_id": "1",
                "instance_type": "testtype" 
            },
        ]

        second_call = [
            {
                "asset_id": "2",
                "attribute_id": "2",
                "args": {"value": "value1"},
                "timestamp": datetime(2012, 1, 1, 17, 0),
                "instance_id": "1",
                "instance_type": "testtype" 
            },
            {
                "asset_id": "2",
                "attribute_id": "2",
                "args": {"value": "value2"},
                "timestamp": datetime(2012, 1, 1, 17, 1),
                "instance_id": "1",
                "instance_type": "testtype" 
            },
            {
                "asset_id": "2",
                "attribute_id": "2",
                "args": {"value": "value3"},
                "timestamp": datetime(2012, 1, 1, 17, 2),
                "instance_id": "1",
                "instance_type": "testtype" 
            }
        ]
        expected_result_first_call = [
            Variable(asset_id="1", attribute_id="1", args={"value": "value1"}, path=None, instance_id="1", instance_type="testtype", timestamp=datetime(2012, 1, 1, 17, 0)),
            Variable(asset_id="1", attribute_id="1", args={"value": "value2"}, path=None, instance_id="1", instance_type="testtype", timestamp=datetime(2012, 1, 1, 17, 1)),
            Variable(asset_id="1", attribute_id="1", args={"value": "value3"}, path=None, instance_id="1", instance_type="testtype", timestamp=datetime(2012, 1, 1, 17, 2))
        ]
        expected_result_second_call = [
            Variable(asset_id="2", attribute_id="2", args={"value": "value1"}, path=None, instance_id="1", instance_type="testtype", timestamp=datetime(2012, 1, 1, 17, 0)),
            Variable(asset_id="2", attribute_id="2", args={"value": "value2"}, path=None, instance_id="1", instance_type="testtype", timestamp=datetime(2012, 1, 1, 17, 1)),
            Variable(asset_id="2", attribute_id="2", args={"value": "value3"}, path=None, instance_id="1", instance_type="testtype", timestamp=datetime(2012, 1, 1, 17, 2))
        ]

        client = MongoClient()
        pipeline_first_call = client._get_pipeline(
            filters={
                "asset_id": {"$eq": "1"},
                "attribute_id": {"$eq": "1"},
                "timestamp": {
                    "$gte": datetime(2012, 1, 1, 17, 0),
                    "$lte": datetime(2012, 1, 1, 18, 0)
                }
            },
            limit=3,
            skip=0,
            sort=[('timestamp', -1)],
            group_id=[],
            group_fields=[]
        )
        pipeline_second_call = client._get_pipeline(
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
            sort=[('timestamp', -1)],
            group_id=[],
            group_fields=[]
        )
        with patch("splight_datalake.mongo.MongoClient._aggregate", side_effect=[first_call, second_call]) as find_call:
            self.assertEqual(client.get(resource_type=Variable, asset_id="1", attribute_id="1", limit_=3, timestamp__gte=datetime(2012, 1, 1, 17, 0), timestamp__lte=datetime(2012, 1, 1, 18, 0)), expected_result_first_call)
            self.assertEqual(client.get(resource_type=Variable, asset_id__in=["2"], attribute_id__contains="2", limit_=3, timestamp__gte=datetime(2012, 1, 1, 17, 0), timestamp__lte=datetime(2012, 1, 1, 18, 0)), expected_result_second_call)
            find_call.assert_has_calls([
                call(
                    collection='default',
                    pipeline=pipeline_first_call,
                    tzinfo=timezone.utc),
                call(
                    collection='default',
                    pipeline=pipeline_second_call,
                    tzinfo=timezone.utc)
            ])

    def test_save_variable(self):
        vars = [
            Variable(asset_id="1", attribute_id="1", instance_id="1", args={"value": "value1"}, timestamp=datetime(2012, 1, 1, 8, 0), instance_type="testtype"),
            Variable(asset_id="2", attribute_id="1", instance_id="1", args={"value": "value1"}, timestamp=datetime(2012, 1, 1, 8, 0), instance_type="testtype"),
            Variable(asset_id="2", attribute_id="2", instance_id="1", args={"value": "value2"}, timestamp=datetime(2012, 1, 1, 8, 0), instance_type="testtype"),
        ]
        expected_data_list = [
            {
                "args": {"value": "value1"},
                "path": None,
                "asset_id": "1",
                "attribute_id": "1",
                "instance_id": "1",
                "timestamp": datetime(2012, 1, 1, 8, 0),
                "instance_type": "testtype"
            },
            {
                "args": {"value": "value1"},
                "path": None,
                "asset_id": "2",
                "attribute_id": "1",
                "instance_id": "1",
                "timestamp": datetime(2012, 1, 1, 8, 0),
                "instance_type": "testtype"
            },
            {
                "args": {"value": "value2"},
                "path": None,
                "asset_id": "2",
                "attribute_id": "2",
                "instance_id": "1",
                "timestamp": datetime(2012, 1, 1, 8, 0),
                "instance_type": "testtype"
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
                "timestamp": datetime(2012, 1, 1, 8, 0),
                "instance_type": "testtype",
                "instance_id" : "1"
            }
        ]
        expected_result = [
            Variable(asset_id="1", attribute_id="1", args={"value": "value1"}, timestamp=datetime(2012, 1, 1, 8, 0), instance_type="testtype", instance_id="1")
        ]
        client = MongoClient()
        pipeline = client._get_pipeline(
            filters={
                "args.value": {"$eq": "value1"}
            },
            limit=50,
            skip=0,
            sort=[('timestamp', -1)],
            group_id=[],
            group_fields=[]
        )
        with patch("splight_datalake.mongo.MongoClient._aggregate", return_value=return_value) as find_call:
            self.assertEqual(client.get(Variable, args__value="value1"), expected_result)
            find_call.assert_called_once_with(
                collection='default',
                pipeline=pipeline,
                tzinfo=timezone.utc
            )

    def test_add_pre_hook(self):
        class ParticularException(Exception): pass
        def foo(*args, **kwargs): raise ParticularException
        client = MongoClient()
        client.add_pre_hook("save", foo)
        with self.assertRaises(ParticularException):
            client.save()

    def test_get_pipelines_group_id_without_group_fields(self):
        client = MongoClient()
        pipeline = client._get_pipeline(
            filters = {"key": 2},
            limit = 2,
            skip = 3,
            sort=[('timestamp', -1)],
            group_id=[
                ('timestamp', 'year'),
                ('timestamp', 'dayOfYear'),
                ('timestamp', 'hour'),
                ('timestamp', 'minute'),
                ('timestamp', 'second'),
            ],
            group_fields=[]
        )
        self.assertEqual(pipeline, [
            {'$match': {'key': 2}},
            {'$group': {
                '_id': {
                    'year-timestamp': {'$year': '$timestamp'},
                    'dayOfYear-timestamp': {'$dayOfYear': '$timestamp'},
                    'hour-timestamp': {'$hour': '$timestamp'},
                    'minute-timestamp': {'$minute': '$timestamp'},
                    'second-timestamp': {'$second': '$timestamp'},
                }, 
                '_root': {'$last': '$$ROOT'}
                }
            },
            {'$replaceRoot': {'newRoot': '$_root'}},
            {'$skip': 3},
            {'$sort': {'timestamp': -1}},
            {'$limit': 2},
        ])

    @parameterized.expand([
        ([None],),
        ([
            None,
            ('timestamp', 'year'),
            ('timestamp', 'dayOfYear'),
            ('timestamp', 'hour'),
            ('timestamp', 'minute'),
            ('timestamp', 'second'),
        ],),
    ])
    def test_get_pipelines_group_id_None(self, group_id):
        client = MongoClient()
        pipeline = client._get_pipeline(
            filters = {"key": 2},
            limit = 2,
            skip = 3,
            sort=[('timestamp', -1)],
            group_id=group_id,
            group_fields=[]
        )
        self.assertEqual(pipeline, [
            {'$match': {'key': 2}},
            {'$group': {
                '_id': None, 
                '_root': {'$last': '$$ROOT'}
                }
            },
            {'$replaceRoot': {'newRoot': '$_root'}},
            {'$skip': 3},
            {'$sort': {'timestamp': -1}},
            {'$limit': 2},
        ])

    def test_get_pipelines_group_fields_without_group_id(self):
        client = MongoClient()
        pipeline = client._get_pipeline(
            filters = {"key": 2},
            limit = 2,
            skip = 3,
            sort=[('timestamp', -1)],
            group_id=[],
            group_fields=[
                ('timestamp', 'last'),
                ('asset_id', 'avg'),
            ]
        )
        self.assertEqual(pipeline, [
            {'$match': {'key': 2}},
            {'$skip': 3},
            {'$sort': {'timestamp': -1}},
            {'$limit': 2},
        ])

    def test_get_pipelines_group_id_with_group_fields(self):
        client = MongoClient()
        pipeline = client._get_pipeline(
            filters = {"key": 2},
            limit = 2,
            skip = 3,
            sort=[('timestamp', -1)],
            group_id=[
                ('timestamp', 'year'),
                ('timestamp', 'dayOfYear'),
                ('timestamp', 'hour'),
                ('timestamp', 'minute'),
                ('timestamp', 'second'),
            ],
            group_fields=[
                ('args.value', 'avg'),
                ('timestamp', 'last')
            ]
        )
        self.assertEqual(pipeline, [
            {'$match': {'key': 2}},
            {'$group': {
                '_id': {
                    'year-timestamp': {'$year': '$timestamp'},
                    'dayOfYear-timestamp': {'$dayOfYear': '$timestamp'},
                    'hour-timestamp': {'$hour': '$timestamp'},
                    'minute-timestamp': {'$minute': '$timestamp'},
                    'second-timestamp': {'$second': '$timestamp'},
                }, 
                '_root': {'$last': '$$ROOT'},
                'agg_args__value': {'$avg': '$args.value'},
                'agg_timestamp': {'$last': '$timestamp'}
                }
            },
            {'$set': {
                '_root.args.value': '$agg_args__value',
                '_root.timestamp': '$agg_timestamp'
            }},
            {'$replaceRoot': {'newRoot': '$_root'}},
            {'$skip': 3},
            {'$sort': {'timestamp': -1}},
            {'$limit': 2},
        ])

    def test_get_components_sizes_gb(self):
        client = MongoClient()
        result = [{
            "_id": "componentid",
            "size": 20096,
        }]
        with patch.object(client.db, "collection_names", return_value=["default"]):
            with patch.object(MongoClient, "_aggregate", return_value=result):
                components_sizes = client.get_components_sizes_gb()
                self.assertEqual(components_sizes, {"componentid": 0.000018715858459472656})