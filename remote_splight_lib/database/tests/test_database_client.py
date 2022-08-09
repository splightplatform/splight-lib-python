from unittest import TestCase
from unittest.mock import patch

from remote_splight_lib.auth import SplightAuthToken
from remote_splight_lib.database import DatabaseClient
from remote_splight_lib.database.client import Session
from splight_models import Attribute

ATTR_ID = "fb3ae667-aa77-4064-b7b4-8181e0fd5477"
ATTR_NAME = "some-attribute"


class MockAttributeResponse:
    def json(self):
        return {
            "id": ATTR_ID,
            "name": ATTR_NAME,
        }

    def raise_for_status(self):
        return None


class MockPaginatedResponse:
    def json(self):
        return {
            "count": 10,
            "next": None,
            "results": [
                {
                    "id": ATTR_ID,
                    "name": ATTR_NAME,
                }
            ],
        }

    def raise_for_status(self):
        return None


class TestDatabaseClient(TestCase):

    def get_client(self):
        client = DatabaseClient()
        return client

    @patch.object(
        Session, "post", autospect=True, return_value=MockAttributeResponse()
    )
    def test_create_new_resource(self, mocked_method):
        client = self.get_client()
        resource = Attribute(name=ATTR_NAME)
        created = client.save(resource)
        mocked_method.assert_called()
        assert created.name == resource.name

    @patch.object(
        Session, "put", autospec=True, return_value=MockAttributeResponse()
    )
    def test_update_resource(self, mocked_method):
        client = self.get_client()
        _ = client.save(Attribute(id=ATTR_ID, name=ATTR_NAME))
        mocked_method.assert_called()

    @patch.object(Session, "delete", autopec=True)
    def test_delete_resource(self, mocked_method):
        client = self.get_client()
        client.delete(resource_type=Attribute, id=ATTR_ID)
        mocked_method.assert_called()

    @patch.object(
        Session, "get", autospec=True, return_value=MockPaginatedResponse()
    )
    def test_count(self, mocked_method):
        client = self.get_client()
        client.count(Attribute)
        mocked_method.assert_called()
