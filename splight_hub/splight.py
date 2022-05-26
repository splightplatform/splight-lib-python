import requests
from client import validate_resource_type
from pydantic import BaseModel
from typing import List, Type
from splight_models.runner import Algorithm, Network, Connector

from splight_hub.abstract import AbstractHubClient
from splight_hub.settings import SPLIGHT_HUB_HOST, SPLIGHT_HUB_TOKEN


class SplightHubClient(AbstractHubClient):
    valid_classes = [Algorithm, Network, Connector]
    
    def __init__(self, *args, **kwargs) -> None:
        super(SplightHubClient, self).__init__(*args, **kwargs)
        self.host = SPLIGHT_HUB_HOST
        self.headers = {}
        if SPLIGHT_HUB_TOKEN:
            self.headers = {'Authorization': f'Token {SPLIGHT_HUB_TOKEN}'}

    def save(self, instance: BaseModel) -> BaseModel:
        raise NotImplementedError

    @validate_resource_type
    def get(self, resource_type: Type, first=False, **kwargs) -> List[BaseModel]:
        url = "/".join([self.host, resource_type.__name__.lower()])
        response = requests.get(url, headers=self.headers)
        assert response.status_code == 200, "Unreachable hub host"
        queryset = [
            resource_type(**v)
            for v in response.json()['results']
        ]
        kwargs = self._validated_kwargs(resource_type, **kwargs)
        queryset = self._filter(queryset, **kwargs)
        return queryset

    def delete(self, resource_type: Type, id: str) -> None:
        raise NotImplementedError
