from uuid import uuid4
from datetime import datetime, timezone
from typing import Dict, List, Type, Tuple

from pydantic import BaseModel
from splight_abstract.hub.abstract import AbstractHubSubClient
from splight_lib import logging
from splight_models import (
    HubComponent,
    HubComponentVersion,
)
from splight_abstract import AbstractHubClient, validate_resource_type


logger = logging.getLogger()


class FakeHubSubClient(AbstractHubSubClient):
    components = [
        HubComponent(id="1", name='Net1', description=None, version='01', input=[], splight_cli_version="0.1.0"),
        HubComponent(id="2", name='Net2', description=None, version='01', input=[], splight_cli_version="0.1.0"),
        HubComponent(id="3", name='Net3', description=None, version='01', input=[], splight_cli_version="0.1.0"),
        HubComponent(id="4", name='Algo1', description=None, version='01', input=[], splight_cli_version="0.1.0"),
        HubComponent(id="5", name='Algo2', description=None, version='01', input=[], splight_cli_version="0.1.0"),
        HubComponent(id="6", name='Conn1', description=None, version='01', input=[], splight_cli_version="0.1.0"),
        HubComponent(
            id="7",
            name="System1",
            description=None,
            version="01",
            input=[],
            splight_cli_version="0.1.0",
        )
    ]
    versions = components
    grouped_versions = components
    database: Dict[Type, List[BaseModel]] = {
        HubComponent: grouped_versions,
        HubComponentVersion: versions,
    }
    valid_classes = [
        HubComponent,
        HubComponentVersion
    ]

    allowed_update_fields = ["verification"]

    def save(self, instance: BaseModel) -> BaseModel:
        raise NotImplementedError

    @validate_resource_type
    def _get(self,
             resource_type: Type,
             first=False,
             limit_: int = -1,
             skip_: int = 0,
             **kwargs) -> List[BaseModel]:
        logger.debug(f"[FAKED] Pulling from hub {resource_type}s")
        queryset = self.database[resource_type]
        kwargs = self._validated_kwargs(resource_type, **kwargs)
        queryset = self._filter(queryset, **kwargs)
        if limit_ != -1:
            queryset = queryset[skip_:skip_ + limit_]

        if first:
            return queryset[0] if queryset else None

        return queryset

    @validate_resource_type
    def delete(self, resource_type: Type, id: str) -> None:
        raise NotImplementedError

    @validate_resource_type
    def update(self, resource_type: Type, id: str, data: Dict) -> BaseModel:
        instance = self.get(resource_type, id=id, first=True)
        if not instance:
            raise ValueError(f"{resource_type} with id {id} not found")
        for field in self.allowed_update_fields:
            if field in data:
                setattr(instance, field, data[field])
        return instance


class FakeHubClient(AbstractHubClient):

    def __init__(self, *args, **kwargs) -> None:
        self._client = FakeHubSubClient()

    def upload(self, data: Dict, files: Dict) -> Tuple:
        component = {
            "id": uuid4(),
            "tenant": "org_agu2n52305",
            "name": data["name"],
            "version": data["version"],
            "splight_cli_version": data["splight_cli_version"],
            "privacy_policy": data["privacy_policy"],
            "verification": data["verification"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_modified": datetime.now(timezone.utc).isoformat(),
            "readme": "some readme",
            "picture": "picture",
            "file": "file",
            "custom_types": [],
            "input": [],
            "output": [],
            "commands": [],
            "deleted": False
        }
        return component, 201

    def download(self, data: Dict) -> Tuple:
        return b"file content", 200

    def random_picture(self) -> Tuple:
        return b"image", 200

    @property
    def all(self) -> AbstractHubSubClient:
        return self._client

    @property
    def mine(self) -> AbstractHubSubClient:
        return self._client

    @property
    def public(self) -> AbstractHubSubClient:
        return self._client

    @property
    def private(self) -> AbstractHubSubClient:
        return self._client

    @property
    def setup(self) -> AbstractHubSubClient:
        return self._client

    @property
    def system(self) -> AbstractHubSubClient:
        return self._client
