import requests
from client import validate_resource_type
from pydantic import BaseModel
from typing import List, Type, Dict
from splight_models import HubAlgorithm, HubNetwork, HubConnector
from splight_models.query import QuerySet
from splight_hub.abstract import AbstractHubClient
from splight_hub.settings import SPLIGHT_HUB_HOST


class SplightHubClient(AbstractHubClient):
    valid_classes = [HubAlgorithm, HubNetwork, HubConnector]

    def __init__(self, token=None, cross_tenant=None, *args, **kwargs) -> None:
        super(SplightHubClient, self).__init__(*args, **kwargs)
        self.host = SPLIGHT_HUB_HOST
        self.headers = {}
        if token:
            self.headers["Authorization"] = token
        if cross_tenant:
            self.headers["X-Organization-ID"] = cross_tenant

    def save(self, instance: BaseModel) -> BaseModel:
        raise NotImplementedError

    @validate_resource_type
    def _get(self, resource_type: Type,
             first=False,
             limit_: int = -1,
             skip_: int = 0,
             **kwargs) -> List[BaseModel]:
        url = "/".join([self.host, resource_type.__name__.lower().replace("hub", "")])
        response = requests.get(url, headers=self.headers)
        assert response.status_code == 200, "Unreachable hub host"
        queryset = [
            resource_type(**v)
            for v in response.json()['results']
        ]
        kwargs = self._validated_kwargs(resource_type, **kwargs)
        queryset = self._filter(queryset, **kwargs)
        if limit_ != -1:
            result = result[skip_:skip_ + limit_]
        if first:
            return queryset[0] if queryset else None
        return queryset

    def delete(self, resource_type: Type, id: str) -> None:
        raise NotImplementedError

    @validate_resource_type
    def update(self, resource_type: Type, id: str, data: Dict) -> BaseModel:
        url = "/".join([self.host, resource_type.__name__.lower().replace("hub", ""), id]) + "/"
        response = requests.patch(url, headers=self.headers, json=data)
        assert response.status_code == 200, f"Couldn't update hub component. {response.status_code}"
        return resource_type(**response.json())
