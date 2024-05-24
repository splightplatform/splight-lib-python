import os

import pytest  # noqa E402
from furl import furl  # noqa E402
from pytest_mock import MockerFixture

from splight_lib.client.database.remote_client import (  # noqa E402
    RemoteDatabaseClient,
    SplightRestClient,
)
from splight_lib.client.exceptions import InvalidModelName  # noqa E402

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
        # autospec=True
    )

    _ = RemoteDatabaseClient(
        base_url=base_url,
        access_id=access_id,
        secret_key=secret_key,
    )

    mock.assert_called_once_with(
        {"Authorization": "Splight access_id secret_key"}
    )


def test_save_without_id(mocker: MockerFixture):
    secret_key = os.getenv("SECRET_KEY")
    access_id = os.getenv("ACCESS_ID")

    client = RemoteDatabaseClient(
        base_url=base_url,
        access_id=access_id,
        secret_key=secret_key,
    )
    mock = mocker.patch.object(
        SplightRestClient,
        "post",
        return_value=MockResponse({"name": "instance_name", "id": "some_id"}),
    )

    mock_instance = {"name": "instance_name"}
    result = client.save("alert", mock_instance)

    # mock_post.assert_called_once()
    mock.assert_called_once()

    assert "id" in result
    assert result["name"] == mock_instance["name"]


def test_save_with_id(mocker: MockerFixture):
    secret_key = os.getenv("SECRET_KEY")
    access_id = os.getenv("ACCESS_ID")

    client = RemoteDatabaseClient(
        base_url=base_url,
        access_id=access_id,
        secret_key=secret_key,
    )

    mock_put = mocker.patch.object(
        SplightRestClient,
        "put",
        return_value=MockResponse(
            {"name": "instance_name", "id": "instance_id"}
        ),
    )

    mock_instance = {"id": "instance_id", "name": "instance_name"}
    result = client.save("alert", mock_instance)
    mock_put.assert_called_once_with(
        furl(f"{base_url}/v2/engine/alert/alerts/instance_id/"),
        json=mock_instance,
    )
    assert result == mock_instance


def test_delete(mocker: MockerFixture):
    secret_key = os.getenv("SECRET_KEY")
    access_id = os.getenv("ACCESS_ID")

    client = RemoteDatabaseClient(
        base_url=base_url,
        access_id=access_id,
        secret_key=secret_key,
    )

    mock_delete = mocker.patch.object(
        SplightRestClient,
        "delete",
        return_value=MockResponse({}),
    )
    client.delete("alert", "instance_id")
    mock_delete.assert_called_once()


def test_delete_invalid_model_name():
    secret_key = os.getenv("SECRET_KEY")
    access_id = os.getenv("ACCESS_ID")

    client = RemoteDatabaseClient(
        base_url=base_url,
        access_id=access_id,
        secret_key=secret_key,
    )

    with pytest.raises(InvalidModelName):
        client.delete("invalid_resource_name", "instance_id")


def test_get_with_id(mocker: MockerFixture):
    secret_key = os.getenv("SECRET_KEY")
    access_id = os.getenv("ACCESS_ID")

    mock_instance_id = "123"
    client = RemoteDatabaseClient(
        base_url=base_url,
        access_id=access_id,
        secret_key=secret_key,
    )

    mock_get = mocker.patch.object(
        SplightRestClient,
        "get",
        return_value=MockResponse(
            {"name": "instance_name", "id": mock_instance_id}
        ),
    )

    result = client._get("alert", id=mock_instance_id)
    mock_get.assert_called_once()
    assert result["id"] == mock_instance_id


def test_get_without_id(mocker: MockerFixture):
    secret_key = os.getenv("SECRET_KEY")
    access_id = os.getenv("ACCESS_ID")

    return_value = MockResponse(
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

    _ = mocker.patch.object(
        SplightRestClient, "get", return_value=return_value
    )
    result = client._get("alert")

    assert result[0]["id"] == "instance_id"
    assert result[0]["name"] == "instance_name"


def test_get_without_id_and_set_first(mocker: MockerFixture):
    secret_key = os.getenv("SECRET_KEY")
    access_id = os.getenv("ACCESS_ID")

    return_value = MockResponse(
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

    _ = mocker.patch.object(
        SplightRestClient, "get", return_value=return_value
    )
    result = client._get("alert", first=True)

    assert result[0]["id"] == "instance_id"
    assert result[0]["name"] == "instance_name"
