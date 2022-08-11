from pytest import MonkeyPatch
MonkeyPatch().setenv("SPLIGHT_ACCESS_ID", "access_id")
MonkeyPatch().setenv("SPLIGHT_SECRET_KEY", "secret_key")

from requests import Session
from unittest import TestCase
from unittest.mock import patch

from remote_splight_lib.storage import StorageClient
from splight_models import StorageFile

FILE_ID = "fb3ae667-aa77-4064-b7b4-8181e0fd5477"
FILE_FILE = "some"


class MockFileResponse:
    def json(self):
        return {
            "id": FILE_ID,
            "file": FILE_FILE,
        }

    def raise_for_status(self):
        return None


class MockPaginatedResponse:
    def json(self):
        return {
            "count": 1,
            "next": None,
            "results": [
                {
                    "id": FILE_ID,
                    "file": FILE_FILE,
                }
            ],
        }

    def raise_for_status(self):
        return None


class TestStorageClient(TestCase):
    def setUp(self) -> None:
        self.client = StorageClient()
        return super().setUp()

    def test_delete_resource(self):
        with self.assertRaises(NotImplementedError):
            self.client.delete(resource_type=StorageFile, id=FILE_ID)

    @patch.object(
        Session, 'get', autospec=True, return_value=MockPaginatedResponse()
    )
    def test_get(self, mocked_method):
        result = self.client.get(StorageFile)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, FILE_ID)
        self.assertEqual(result[0].file, FILE_FILE)
        mocked_method.assert_called()