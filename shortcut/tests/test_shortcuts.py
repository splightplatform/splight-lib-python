from django.test import TestCase
from splight_models import Variable
from splight_lib.database import *
from splight_lib.datalake import DatalakeClient
from splight_lib.communication import *
from unittest.mock import  patch, call
from ..asset_attributes import _get_asset_attribute_mapping, asset_get, asset_set, NoDefaultValue
import os

class TestShortcuts(TestCase):
    def setUp(self):
        self.namespace = "default"
        self.database = DatabaseClient(self.namespace)
        self.datalake = DatalakeClient(self.namespace)
        
        self.asset = self.database.save(Asset(name="Asset1", description="test_description"))
        self.attribute = self.database.save(Attribute(name="Attribute11"))
        self.network = self.database.save(Network(name="Network1"))
        self.client_connector = self.database.save(ClientConnector(host="123", port=123, protocol="asd", network_id=self.network.id))
        self.server_connector = self.database.save(ServerConnector(host="123", port=123, protocol="asd", network_id=self.network.id, external_port="123"))

        self.variable = Variable(asset_id=self.asset.id, attribute_id=self.attribute.id, args=dict({"value": 1}))
        return super().setUp()
        

    def test_multiple_mappings(self):
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
            mock.assert_has_calls([call(Variable, instances=[Variable(asset_id=self.asset.id,attribute_id=self.attribute.id,args=dict())], fields=['asset_id', 'attribute_id'])]*2)


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
            mock_send.assert_called_once_with({"action":Action.WRITE, "variables":[Variable(asset_id=self.asset.id, attribute_id=self.attribute.id, args=dict(value=VALUE1)).dict()]})

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