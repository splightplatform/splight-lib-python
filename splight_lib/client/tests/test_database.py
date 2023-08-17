from unittest.mock import patch  # noqa E402

import pytest  # noqa E402
from furl import furl  # noqa E402

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


@patch.object(
    SplightRestClient,
    "post",
    return_value=MockResponse({"name": "instance_name", "id": "some_id"}),
)
def test_save_without_id(mock_post):
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


@patch.object(
    SplightRestClient,
    "put",
    return_value=MockResponse({"name": "instance_name", "id": "instance_id"}),
)
def test_save_with_id(mock_put):
    client = RemoteDatabaseClient(
        base_url=base_url,
        access_id=access_id,
        secret_key=secret_key,
    )

    mock_instance = {"id": "instance_id", "name": "instance_name"}
    result = client.save("alert", mock_instance)

    mock_put.assert_called_once_with(
        furl(f"{base_url}/v2/engine/alert/alerts/instance_id/"),
        json=mock_instance,
    )
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


@patch.object(SplightRestClient, "get")
def test_get_with_id(mock_get):
    mock_instance_id = "123"
    mock_get.return_value = MockResponse(
        {"name": "instance_name", "id": mock_instance_id}
    )
    client = RemoteDatabaseClient(
        base_url=base_url,
        access_id=access_id,
        secret_key=secret_key,
    )

    result = client._get("alert", id=mock_instance_id)
    mock_get.assert_called_once()
    assert result["id"] == mock_instance_id


@patch.object(SplightRestClient, "get")
def test_get_without_id(mock_get):
    mock_get.return_value = MockResponse(
        {
            "results": [{"name": "instance_name", "id": "instance_id"}],
            "next": None,
        }
    )
    client = RemoteDatabaseClient(
        base_url=base_url,
        access_id=access_id,
        secret_key=secret_key,
    )
    result = client._get("alert")

    assert result[0]["id"] == "instance_id"
    assert result[0]["name"] == "instance_name"


@patch.object(SplightRestClient, "get")
def test_get_without_id_and_set_first(mock_get):
    mock_get.return_value = MockResponse(
        {
            "results": [{"name": "instance_name", "id": "instance_id"}],
            "next": None,
        }
    )
    client = RemoteDatabaseClient(
        base_url=base_url,
        access_id=access_id,
        secret_key=secret_key,
    )
    result = client._get("alert", first=True)

    assert result[0]["id"] == "instance_id"
    assert result[0]["name"] == "instance_name"
