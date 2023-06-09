import os
from unittest.mock import patch  # noqa E402

import pandas as pd  # noqa E402
from splight_lib.client.datalake import RemoteDatalakeClient  # noqa F402

base_url = "http://test.com"
access_id = os.environ["SPLIGHT_ACCESS_ID"]
secret_key = os.environ["SPLIGHT_SECRET_KEY"]


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


@patch("splight_lib.client.datalake.remote_client.SplightRestClient")
def test_save(mock_rest_client):
    mock_rest_client.return_value.post.return_value.raise_for_status.return_value = (
        None
    )
    client = RemoteDatalakeClient(
        base_url=base_url,
        access_id=access_id,
        secret_key=secret_key,
    )
    collection = "collection_name"
    instances = [{"key": "value"}]
    result = client.save(collection=collection, instances=instances)
    mock_rest_client.return_value.post.assert_called_once()
    assert result == instances


@patch("splight_lib.client.datalake.remote_client.SplightRestClient")
def test_raw_get(mock_rest_client):
    response_data = {"results": [{"key": "value"}]}
    mock_rest_client.return_value.get.return_value.json.return_value = (
        response_data
    )
    mock_rest_client.return_value.get.return_value.raise_for_status.return_value = (
        None
    )
    client = RemoteDatalakeClient(base_url, access_id, secret_key)
    collection = "collection_name"
    result = client._raw_get("resource", collection)
    mock_rest_client.return_value.get.assert_called_once()
    assert result == response_data["results"]


@patch("splight_lib.client.datalake.remote_client.SplightRestClient")
def test_delete(mock_rest_client):
    mock_rest_client.return_value.delete.return_value.raise_for_status.return_value = (
        None
    )
    client = RemoteDatalakeClient(base_url, access_id, secret_key)
    collection = "collection_name"
    client.delete(collection)
    mock_rest_client.return_value.delete.assert_called_once()


@patch("splight_lib.client.datalake.remote_client.SplightRestClient")
def test_save_dataframe(mock_rest_client):
    mock_rest_client.return_value.post.return_value.raise_for_status.return_value = (
        None
    )
    client = RemoteDatalakeClient(base_url, access_id, secret_key)
    collection = "collection_name"
    dataframe = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    client.save_dataframe(collection, dataframe)
    mock_rest_client.return_value.post.assert_called_once()


@patch("splight_lib.client.datalake.remote_client.SplightRestClient")
def test_create_index(mock_rest_client):
    mock_rest_client.return_value.post.return_value.raise_for_status.return_value = (
        None
    )
    client = RemoteDatalakeClient(base_url, access_id, secret_key)
    collection = "collection_name"
    indexes = [{"key": 1}]
    client.create_index(collection, indexes)
    mock_rest_client.return_value.post.assert_called_once()


@patch("splight_lib.client.datalake.remote_client.SplightRestClient")
def test_raw_aggregate(mock_rest_client):
    response_data = [{"key": "value"}]
    mock_rest_client.return_value.post.return_value.json.return_value = (
        response_data
    )
    mock_rest_client.return_value.post.return_value.raise_for_status.return_value = (
        None
    )
    client = RemoteDatalakeClient(base_url, access_id, secret_key)
    collection = "collection_name"
    pipeline = [{"$match": {"key": "value"}}]
    result = client.raw_aggregate(collection, pipeline)
    mock_rest_client.return_value.post.assert_called_once()
    assert result == response_data
