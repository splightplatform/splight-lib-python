import os

os.environ["SPLIGHT_ACCESS_ID"] = "access_id"
os.environ["SPLIGHT_SECRET_KEY"] = "secret_key"

from typing import Optional  # noqa: E402
from unittest.mock import patch  # noqa: E402
from uuid import uuid4  # noqa: E402

import pytest  # noqa: E402

from splight_lib.client.database.local_client import (  # noqa: E402
    LocalDatabaseClient,
)
from splight_lib.models.base import SplightDatabaseBaseModel  # noqa: E402
from splight_lib.settings import settings  # noqa: E402

settings.configure(LOCAL_ENVIRONMENT=True)


class Resource(SplightDatabaseBaseModel):
    id: Optional[str]
    name: str
    age: int
    saber_color: str


RESOURCE_LIST = [
    {
        "id": str(uuid4()),
        "name": "DartMaul",
        "age": 34,
        "saber_color": "red",
    },
    {
        "id": str(uuid4()),
        "name": "Luke",
        "age": 23,
        "saber_color": "green",
    },
    {
        "id": str(uuid4()),
        "name": "MaceWindu",
        "age": 60,
        "saber_color": "violet",
    },
    {
        "id": str(uuid4()),
        "name": "ObiWan",
        "age": 45,
        "saber_color": "blue",
    },
]


@patch.object(LocalDatabaseClient, "_get", return_value=RESOURCE_LIST)
def test_list(mock):
    instances = Resource.list()
    mock.assert_called_with(Resource.__name__)
    assert all([isinstance(item, Resource) for item in instances])
    assert all(
        [item.id == RESOURCE_LIST[idx]["id"]]
        for idx, item in enumerate(instances)
    )


@patch.object(LocalDatabaseClient, "_get", return_value=RESOURCE_LIST)
def test_list_first(mock):
    instances = Resource.list(first=True)
    mock.assert_called_with(Resource.__name__, first=True)
    assert all([isinstance(item, Resource) for item in instances])
    assert all(
        [item.id == RESOURCE_LIST[idx]["id"]]
        for idx, item in enumerate(instances)
    )


@pytest.mark.parametrize(
    "instance_dict",
    RESOURCE_LIST,
)
def test_retrieve(instance_dict):
    with patch.object(
        LocalDatabaseClient, "_get", return_value=instance_dict
    ) as mock:
        instance = Resource.retrieve(instance_dict["id"])
        mock.assert_called_with(Resource.__name__, id=instance.id, first=True)
        assert instance.model_dump() == instance_dict


@pytest.mark.parametrize(
    "instance_dict",
    RESOURCE_LIST,
)
def test_save_with_id(instance_dict):
    with patch.object(
        LocalDatabaseClient, "save", return_value=instance_dict
    ) as mock:
        resource = Resource.model_validate(instance_dict)
        resource.save()
        mock.assert_called_with(Resource.__name__, instance_dict)
        assert resource.model_dump() == instance_dict


@pytest.mark.parametrize(
    "instance_dict",
    RESOURCE_LIST,
)
def test_save_without_id(instance_dict):
    with patch.object(
        LocalDatabaseClient, "save", return_value=instance_dict
    ) as mock:
        resource = Resource.model_validate(instance_dict)
        resource.id = None
        resource_dict = resource.model_dump(exclude_none=True)
        resource.save()
        mock.assert_called_with(Resource.__name__, resource_dict)
        assert resource.model_dump() == instance_dict


@pytest.mark.parametrize(
    "instance_dict",
    RESOURCE_LIST,
)
def test_delete(instance_dict):
    with patch.object(
        LocalDatabaseClient, "delete", return_value=None
    ) as mock:
        resource = Resource.model_validate(instance_dict)
        resource.delete()
        mock.assert_called_with(
            resource_name=Resource.__name__, id=resource.id
        )
