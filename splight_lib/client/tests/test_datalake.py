import os

from pytest_mock import MockerFixture

from splight_lib.client.datalake import SyncRemoteDatalakeClient  # noqa E402
from splight_lib.client.datalake.remote_client import (  # noqa E402
    SplightRestClient,
)

base_url = "http://test.com"
os.environ["ACCESS_ID"] = "access_id"
os.environ["SECRET_KEY"] = "secret_key"


class MockResponse:
    status_code = 200

    def __init__(self, json_data):
        self.json_data = json_data

    @property
    def is_error(self) -> bool:
        return False if self.status_code < 400 else True

    def raise_for_status(self):
        return None

    def json(self):
        return self.json_data


def test_initialization(mocker: MockerFixture):
    secret_key = os.getenv("SECRET_KEY")
    access_id = os.getenv("ACCESS_ID")

    mock = mocker.patch.object(
        SplightRestClient,
        "update_headers",
        return_value=None,
    )
    _ = SyncRemoteDatalakeClient(
        base_url=base_url,
        access_id=access_id,
        secret_key=secret_key,
    )

    mock.assert_called_once_with(
        {"Authorization": "Splight access_id secret_key"}
    )


def test_save(mocker: MockerFixture):
    secret_key = os.getenv("SECRET_KEY")
    access_id = os.getenv("ACCESS_ID")

    client = SyncRemoteDatalakeClient(
        base_url=base_url,
        access_id=access_id,
        secret_key=secret_key,
    )
    mock_post = mocker.patch.object(
        SplightRestClient,
        "post",
        return_value=MockResponse(({"key": "value"})),
    )
    collection = "collection_name"
    instances = [{"key": "value"}]
    records = {"collection": collection, "records": instances}
    result = client.save(records)
    mock_post.assert_called_once()
    assert result == instances
