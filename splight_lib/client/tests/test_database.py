import os
from unittest.mock import patch

import pytest
from splight_lib.client.database.remote_client import (  # noqa E402
    RemoteDatabaseClient,
    SplightRestClient,
)
from splight_lib.client.exceptions import InvalidModelName  # noqa E402

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


@patch("splight_lib.client.database.remote_client.SplightAuthToken")
@patch("splight_lib.client.database.remote_client.SplightRestClient")
def test_initialization(mock_rest_client, mock_auth_token):
    client = RemoteDatabaseClient(
        base_url=base_url,
        access_id=access_id,
        secret_key=secret_key,
    )

    mock_auth_token.assert_called_once_with(
        access_key=access_id, secret_key=secret_key
    )
    assert client._base_url.url == base_url
    mock_rest_client().update_headers.assert_called_once()


@patch.object(SplightRestClient, "post")
def test_save_without_id(mock_post):
    mock_response = MockResponse({"name": "instance_name", "id": "some_id"})
    mock_post.return_value = mock_response

    client = RemoteDatabaseClient(
        base_url=base_url,
        access_id=access_id,
        secret_key=secret_key,
    )

    mock_instance = {"name": "instance_name"}
    result = client.save("alert", mock_instance)

    mock_post.assert_called_once()

    assert "id" in result
    assert result["name"] == mock_instance["name"]


@patch.object(RemoteDatabaseClient, "_update")
@patch.object(SplightRestClient, "post")
def test_save_with_id(mock_post, mock_update):
    mock_post.return_value = MockResponse(
        {"name": "instance_1", "id": "instance_id"}
    )
    mock_update.return_value = {"name": "instance_name", "id": "instance_id"}

    client = RemoteDatabaseClient(
        base_url=base_url,
        access_id=access_id,
        secret_key=secret_key,
    )

    mock_instance = {"id": "instance_id", "name": "instance_name"}
    result = client.save("alert", mock_instance)

    mock_update.assert_called_once_with("alert", "instance_id", mock_instance)
    assert result == mock_instance


@patch.object(SplightRestClient, "delete")
def test_delete(mock_delete):
    client = RemoteDatabaseClient(
        base_url=base_url,
        access_id=access_id,
        secret_key=secret_key,
    )
    client.delete("alert", "instance_id")
    mock_delete.assert_called_once()


def test_delete_invalid_model_name():
    client = RemoteDatabaseClient(
        base_url=base_url,
        access_id=access_id,
        secret_key=secret_key,
    )

    with pytest.raises(InvalidModelName):
        client.delete("invalid_resource_name", "instance_id")


@patch.object(RemoteDatabaseClient, "_retrieve_single")
def test_get_with_id(mock_retrieve):
    client = RemoteDatabaseClient(
        base_url=base_url,
        access_id=access_id,
        secret_key=secret_key,
    )

    mock_instance_id = "123"
    client._get("alert", id=mock_instance_id)
    mock_retrieve.assert_called_once_with("alert", id=mock_instance_id)


@patch.object(RemoteDatabaseClient, "_retrieve_multiple")
def test_get_without_id(mock_retrieve):
    client = RemoteDatabaseClient(
        base_url=base_url,
        access_id=access_id,
        secret_key=secret_key,
    )
    client._get("alert")
    mock_retrieve.assert_called_once_with("alert", first=False)


@patch.object(RemoteDatabaseClient, "_retrieve_multiple")
def test_get_without_id_and_set_first(mock_retrieve):
    client = RemoteDatabaseClient(
        base_url=base_url,
        access_id=access_id,
        secret_key=secret_key,
    )
    client._get("alert", first=True)
    mock_retrieve.assert_called_once_with("alert", first=True)
