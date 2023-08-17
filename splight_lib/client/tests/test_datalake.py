import os
from unittest.mock import Mock, patch  # noqa E402

import pandas as pd  # noqa E402

from splight_lib.client.datalake import RemoteDatalakeClient  # noqa E402
from splight_lib.client.datalake.remote_client import (  # noqa E402
    SplightRestClient,
)

base_url = "http://test.com"
access_id = "access_id"
secret_key = "secret_key"


class MockResponse:
    status_code = 200

    def __init__(self, json_data):
        self.json_data = json_data

    def raise_for_status(self):
        return None

    def json(self):
        return self.json_data


@patch("splight_lib.client.datalake.remote_client.SplightAuthToken")
@patch("splight_lib.client.datalake.remote_client.SplightRestClient")
def test_initialization(mock_rest_client, mock_auth_token):
    client = RemoteDatalakeClient(
        base_url=base_url,
        access_id=access_id,
        secret_key=secret_key,
    )

    mock_auth_token.assert_called_once_with(
        access_key=access_id, secret_key=secret_key
    )
    mock_rest_client.assert_called_once()


@patch.object(
    SplightRestClient, "post", return_value=MockResponse(({"key": "value"}))
)
def test_save(mock_post):
    client = RemoteDatalakeClient(
        base_url=base_url,
        access_id=access_id,
        secret_key=secret_key,
    )
    collection = "collection_name"
    instances = [{"key": "value"}]
    result = client.save(collection=collection, instances=instances)
    mock_post.assert_called_once()
    assert result == instances


@patch.object(
    SplightRestClient,
    "get",
    return_value=MockResponse({"results": [{"key": "value"}]}),
)
def test_raw_get(mock_get):
    client = RemoteDatalakeClient(base_url, access_id, secret_key)
    collection = "collection_name"
    result = client._raw_get("resource", collection)
    mock_get.assert_called_once()
    assert result == [{"key": "value"}]


@patch.object(SplightRestClient, "delete", return_value=MockResponse(None))
def test_delete(mock_delete):
    client = RemoteDatalakeClient(base_url, access_id, secret_key)
    collection = "collection_name"
    client.delete(collection)
    mock_delete.assert_called_once()


@patch.object(SplightRestClient, "post", return_value=MockResponse(None))
def test_save_dataframe(mock_post):
    client = RemoteDatalakeClient(base_url, access_id, secret_key)
    collection = "collection_name"
    dataframe = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    client.save_dataframe(collection, dataframe)
    mock_post.assert_called_once()


@patch.object(SplightRestClient, "post", return_value=MockResponse(None))
def test_create_index(mock_post):
    client = RemoteDatalakeClient(base_url, access_id, secret_key)
    collection = "collection_name"
    indexes = [{"key": 1}]
    client.create_index(collection, indexes)
    mock_post.assert_called_once()


@patch.object(
    SplightRestClient, "post", return_value=MockResponse([{"key": "value"}])
)
def test_raw_aggregate(mock_post):
    client = RemoteDatalakeClient(base_url, access_id, secret_key)
    collection = "collection_name"
    pipeline = [{"$match": {"key": "value"}}]
    result = client.raw_aggregate(collection, pipeline)
    mock_post.assert_called_once()
    assert result == [{"key": "value"}]
