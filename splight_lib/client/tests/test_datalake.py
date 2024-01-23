import os

import pandas as pd  # noqa E402
from pytest_mock import MockerFixture

from splight_lib.client.datalake import RemoteDatalakeClient  # noqa E402
from splight_lib.client.datalake.remote_client import (  # noqa E402
    SplightRestClient,
)
from splight_lib.client.datalake.schemas import DataRequest

base_url = "http://test.com"
os.environ["ACCESS_ID"] = "access_id"
os.environ["SECRET_KEY"] = "secret_key"


class MockResponse:
    status_code = 200

    def __init__(self, json_data):
        self.json_data = json_data

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
    client = RemoteDatalakeClient(
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

    client = RemoteDatalakeClient(
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
    result = client.save(collection=collection, instances=instances)
    mock_post.assert_called_once()
    assert result == instances


def test_raw_get(mocker: MockerFixture):
    secret_key = os.getenv("SECRET_KEY")
    access_id = os.getenv("ACCESS_ID")

    client = RemoteDatalakeClient(base_url, access_id, secret_key)

    mock_get = mocker.patch.object(
        SplightRestClient,
        "get",
        return_value=MockResponse({"results": [{"key": "value"}]}),
    )
    data_request = DataRequest(
        collection="default_collection",
        traces=[
            {
                "ref_id": "output",
                "type": "QUERY",
                "pipeline": [
                    {
                        "$match": {
                            "asset": "a",
                            "attribute": "b",
                        }
                    }
                ],
                "expression": None,
            }
        ],
    )
    result = client.raw_get(data_request)
    mock_get.assert_called_once()
    assert result == [{"key": "value"}]


def test_delete(mocker: MockerFixture):
    secret_key = os.getenv("SECRET_KEY")
    access_id = os.getenv("ACCESS_ID")

    client = RemoteDatalakeClient(base_url, access_id, secret_key)
    mock_delete = mocker.patch.object(
        SplightRestClient,
        "delete",
        return_value=MockResponse(None),
    )
    collection = "collection_name"
    client.delete(collection)
    mock_delete.assert_called_once()
