from django.test import TestCase
from shortcut.exceptions import ShortcutException
from splight_lib.storage import StorageClient
from splight_models import Variable
from splight_lib.database import DatabaseClient
from splight_lib.datalake import DatalakeClient
from splight_lib.communication import *
from splight_models import *
from unittest.mock import patch, call
from ..asset_attributes import _get_asset_attribute_mapping, asset_get, asset_set, NoDefaultValue, asset_load_history


class TestAssetAttributes(TestCase):
    def setUp(self):
        self.namespace = "default"
        self.database = DatabaseClient(self.namespace)
        self.datalake = DatalakeClient(self.namespace)
        self.storage = StorageClient(self.namespace)

        self.asset = self.database.save(Asset(name="Asset1", description="test_description"))
        self.attribute = self.database.save(Attribute(name="Attribute11"))
        self.network = self.database.save(Network(name="Network1", version='openvpn-0_2'))
        self.client_connector = self.database.save(Connector(name="Client connector", description="Description", version="dnp3-0_2"))
        self.server_connector = self.database.save(Connector(name="Server connector", description="Description", version="dnp3-0_2"))

        self.variable = Variable(asset_id=self.asset.id, attribute_id=self.attribute.id, args=dict({"value": 1}))
        return super().setUp()

    def test_multiple_mappings(self):
        # the mapping (asset,attribute) must be unique among all mappings of any types
        client_mapping = self.database.save(ClientMapping(asset_id=self.asset.id, attribute_id=self.attribute.id, connector_id=self.client_connector.id, path="2/1"))
        self.assertEqual(isinstance(client_mapping, ClientMapping), True)
        client_mapping.path = "3/1"
        # update same mapping
        self.database.save(client_mapping)

        with self.assertRaises(Exception):
            self.database.save(ClientMapping(asset_id=self.asset.id, attribute_id=self.attribute.id, connector_id=self.client_connector.id, path="2/1"))
        with self.assertRaises(Exception):
            self.database.save(ValueMapping(asset_id=self.asset.id, attribute_id=self.attribute.id, value=1))
        with self.assertRaises(Exception):
            # other mapping type with same id
            self.database.save(ValueMapping(id=client_mapping.id, asset_id=self.asset.id, attribute_id=self.attribute.id, value=1))
        with self.assertRaises(Exception):
            self.database.save(ReferenceMapping(asset_id=self.asset.id, attribute_id=self.attribute.id, ref_asset_id=self.asset.id, ref_attribute_id=self.attribute.id))

    def test_get_asset_attribute_mapping(self):
        mapping = self.database.save(ClientMapping(asset_id=self.asset.id, attribute_id=self.attribute.id, connector_id=self.client_connector.id, path="2/1"))
        result = _get_asset_attribute_mapping(self.asset.id, self.attribute.id, self.database)
        self.assertEqual(result, mapping)
        self.database.delete(ClientMapping, mapping.id)
        asset_1 = self.database.save(Asset(name="Asset_1"))
        p = self.database.save(Attribute(name="p"))
        asset_2 = self.database.save(Asset(name="Asset_2"))
        q = self.database.save(Attribute(name="q"))
        reference_mapping0 = self.database.save(ReferenceMapping(asset_id=self.asset.id, attribute_id=self.attribute.id, ref_asset_id=asset_1.id, ref_attribute_id=p.id))
        reference_mapping1 = self.database.save(ReferenceMapping(asset_id=asset_1.id, attribute_id=p.id, ref_asset_id=asset_2.id, ref_attribute_id=q.id))
        value_mapping0 = self.database.save(ValueMapping(asset_id=asset_2.id, attribute_id=q.id, value=123))
        result = _get_asset_attribute_mapping(self.asset.id, self.attribute.id, self.database)
        self.assertEqual(result, value_mapping0)

    def test_asset_get_empty_cases(self):
        with self.assertRaises(AttributeError):
            result = asset_get(self.asset.id, self.attribute.id, self.namespace, NoDefaultValue)
        result = asset_get(self.asset.id, self.attribute.id, self.namespace, default=4)
        self.assertEqual(result, 4)
        result = asset_get(self.asset.id, self.attribute.id, self.namespace, default="default")
        self.assertEqual(result, "default")
        result = asset_get(self.asset.id, self.attribute.id, self.namespace, default=None)
        self.assertEqual(result, None)

    def test_asset_get(self):
        with patch.object(DatalakeClient, "get") as mock:
            mock.side_effect = [
                [],
                [Variable(asset_id=self.asset.id, attribute_id=self.attribute.id, args=dict({"value": 123}))]
            ]
            # No mapping case with default
            result = asset_get(self.asset.id, self.attribute.id, self.namespace, None)
            self.assertEqual(result, None)

            # No mapping case without default
            with self.assertRaises(AttributeError):
                result = asset_get(self.asset.id, self.attribute.id, self.namespace)

            client_mapping = self.database.save(ClientMapping(asset_id=self.asset.id, attribute_id=self.attribute.id, connector_id=self.client_connector.id, path="2/1"))

            # Datalake returns empty case
            result = asset_get(self.asset.id, self.attribute.id, self.namespace, None)
            self.assertEqual(result, None)

            result = asset_get(self.asset.id, self.attribute.id, self.namespace)
            self.assertEqual(result, 123)
            mock.assert_has_calls([call(Variable, asset_id=self.asset.id, attribute_id=self.attribute.id)] * 2)

    def test_asset_set(self):
        VALUE1 = 111
        VALUE2 = 314
        VALUE3 = 245
        VALUE4 = {"asd": "asd"}
        with patch.object(ExternalCommunicationClient, 'send') as mock_send:
            with self.assertRaises(AttributeError):
                asset_set(self.asset.id, self.attribute.id, VALUE1, self.namespace)

            client_mapping = self.database.save(ClientMapping(asset_id=self.asset.id, attribute_id=self.attribute.id, connector_id=self.client_connector.id, path="2/1"))
            asset_set(self.asset.id, self.attribute.id, VALUE1, self.namespace)
            self.assertEqual(mock_send.call_args[0][0]["action"], Action.WRITE)
            self.assertEqual(len(mock_send.call_args[0][0]["variables"]), 1)
            self.assertEqual(mock_send.call_args[0][0]["variables"][0]["asset_id"], self.asset.id)
            self.assertEqual(mock_send.call_args[0][0]["variables"][0]["attribute_id"], self.attribute.id)
            self.assertDictEqual(mock_send.call_args[0][0]["variables"][0]["args"], dict(value=VALUE1))

            self.database.delete(ClientMapping, client_mapping.id)
            value_mapping = self.database.save(ValueMapping(asset_id=self.asset.id, attribute_id=self.attribute.id, value=VALUE2))

            asset_set(self.asset.id, self.attribute.id, VALUE3, self.namespace)
            value_mapping = self.database.get(ValueMapping, asset_id=self.asset.id, attribute_id=self.attribute.id)[0]
            self.assertEqual(value_mapping.value, str(VALUE3))

            self.database.delete(ValueMapping, value_mapping.id)
            value_mapping = self.database.save(ValueMapping(asset_id=self.asset.id, attribute_id=self.attribute.id, value=VALUE2))

            asset_set(self.asset.id, self.attribute.id, VALUE4, self.namespace)
            value_mapping = self.database.get(ValueMapping, asset_id=self.asset.id, attribute_id=self.attribute.id)[0]
            self.assertEqual(value_mapping.value, str(VALUE4))

    def test_asset_load_history_raises(self):
        rows = [
            ('2018-01-02', 21.5, 'AlgunaCategoria', 12.2),
            ('2018-01-03', 22.5, 'AlgunaCategoria', 13.5),
            ('2018-01-04', 21.6, 'AlgunaCategoria', 15),
        ]
        dataframe = pd.DataFrame(
            data=rows,
            columns=['date', 'value', 'category', 'another_value']
        )
        with self.assertRaises(ShortcutException):
            asset_load_history(dataframe, self.database, self.datalake)
        with self.assertRaises(ShortcutException):
            asset_load_history(dataframe, self.database, self.datalake, asset_id="123")

    def test_asset_load_history_by_asset_id(self):
        rows = [
            ('2018-01-02', 21.5, 'AlgunaCategoria', 12.2),
            ('2018-01-03 14:00', 22.5, 'AlgunaCategoria', 13.5),
            ('2018-01-03', 22.5, 'OtraCategoria', 13.5),
            ('2018-01-04', 21.6, 'AlgunaCategoria', 15),
        ]
        dataframe = pd.DataFrame(
            data=rows,
            columns=['timestamp', 'value', 'category', 'another_value']
        )
        asset_id = "123"
        result = asset_load_history(dataframe, self.database, self.datalake, asset_id=asset_id, attribute_name_cols=["another_value"])
        attribute = self.database.get(Attribute, name="another_value")[0]
        self.assertIsNotNone(attribute)
        self.assertTrue(all(v.asset_id == '123' for v in result))
        self.assertTrue(all(v.attribute_id == attribute.id for v in result))
        self.assertEqual([{'value': 12.2}, {'value': 13.5}, {'value': 13.5}, {'value': 15}], [v.args for v in result])

    def test_asset_load_history_by_attribute_id(self):
        rows = [
            ('2018-01-02', 21.5, 'AlgunaCategoria', 12.2),
            ('2018-01-03 14:00', 22.5, 'AlgunaCategoria', 13.5),
            ('2018-01-03', 22.5, 'OtraCategoria', 13.5),
            ('2018-01-04', 21.6, 'AlgunaCategoria', 15),
        ]
        dataframe = pd.DataFrame(
            data=rows,
            columns=['timestamp', 'value', 'category', 'another_value']
        )
        asset_id = "123"
        attribute_id = "456"
        result = asset_load_history(dataframe, self.database, self.datalake, asset_id=asset_id, attribute_id=attribute_id)
        self.assertTrue(all(v.asset_id == asset_id for v in result))
        self.assertTrue(all(v.attribute_id == attribute_id for v in result))
        self.assertEqual([
            {'value': 21.5, 'category': 'AlgunaCategoria', 'another_value': 12.2},
            {'value': 22.5, 'category': 'AlgunaCategoria', 'another_value': 13.5},
            {'value': 22.5, 'category': 'OtraCategoria', 'another_value': 13.5},
            {'value': 21.6, 'category': 'AlgunaCategoria', 'another_value': 15}
        ], [v.args for v in result])

    def test_asset_load_history_by_asset_name_col(self):
        rows = [
            ('2018-01-02', 21.5, 'AlgunaCategoria', 12.2),
            ('2018-01-03 14:00', 22.5, 'AlgunaCategoria', 13.5),
            ('2018-01-03', 22.5, 'OtraCategoria', 13.5),
            ('2018-01-04', 21.6, 'AlgunaCategoria', 15),
        ]
        dataframe = pd.DataFrame(
            data=rows,
            columns=['timestamp', 'value', 'category', 'another_value']
        )
        result = asset_load_history(dataframe, self.database, self.datalake, asset_name_cols=["category"], attribute_name_cols=["value", "another_value"])
        attribute_1 = self.database.get(Attribute, name="value")[0]
        attribute_2 = self.database.get(Attribute, name="another_value")[0]
        asset_1 = self.database.get(Asset, name="AlgunaCategoria")[0]
        asset_2 = self.database.get(Asset, name="OtraCategoria")[0]
        self.assertIsNotNone(attribute_1)
        self.assertIsNotNone(attribute_2)
        self.assertIsNotNone(asset_1)
        self.assertIsNotNone(asset_2)
        self.assertEqual([
                {'value': 21.5},
                {'value': 22.5},
                {'value': 22.5},
                {'value': 21.6},
                {'value': 12.2},
                {'value': 13.5},
                {'value': 13.5},
                {'value': 15.0}
            ], [v.args for v in result]
        )
        self.assertEqual([
                asset_1.id,
                asset_1.id,
                asset_2.id,
                asset_1.id,
                asset_1.id,
                asset_1.id,
                asset_2.id,
                asset_1.id
            ],
            [v.asset_id for v in result]
        )
        self.assertEqual([
                attribute_1.id,
                attribute_1.id,
                attribute_1.id,
                attribute_1.id,
                attribute_2.id,
                attribute_2.id,
                attribute_2.id,
                attribute_2.id,
            ],
            [v.attribute_id for v in result]
        )
