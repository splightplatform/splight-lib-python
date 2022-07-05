import requests
from client import validate_resource_type
from pydantic import BaseModel
from typing import List, Type
from splight_models import HubAlgorithm, HubNetwork, HubConnector

from splight_hub.abstract import AbstractHubClient
from splight_hub.settings import SPLIGHT_HUB_HOST


class SplightHubClient(AbstractHubClient):
    valid_classes = [HubAlgorithm, HubNetwork, HubConnector]
    
    def __init__(self, token=None, *args, **kwargs) -> None:
        super(SplightHubClient, self).__init__(*args, **kwargs)
        self.host = SPLIGHT_HUB_HOST
        self.headers = {}
        if token:
            self.headers = {'Authorization': token}

    def save(self, instance: BaseModel) -> BaseModel:
        raise NotImplementedError

    @validate_resource_type
    def get(self, resource_type: Type, first=False, **kwargs) -> List[BaseModel]:
        url = "/".join([self.host, resource_type.__name__.lower().replace("hub","")])
        response = requests.get(url, headers=self.headers)
        assert response.status_code == 200, "Unreachable hub host"
        queryset = [
            resource_type(**v)
            for v in response.json()['results']
        ]
        kwargs = self._validated_kwargs(resource_type, **kwargs)
        queryset = self._filter(queryset, **kwargs)

        if first:
            return queryset[0] if queryset else None
        return queryset

    def delete(self, resource_type: Type, id: str) -> None:
        raise NotImplementedError

    def set_impact(self, id: str, impact: int) -> None:
        url = "/".join([self.host, "set-impact"]) + "/"
        response = requests.post(url, headers=self.headers, json={"id": id, "impact": impact})
        assert response.status_code == 200, f"Couldn't set impact. {response.status_code}"

    def set_verification(self, id: str, verification: int) -> None:
        url = "/".join([self.host, "set-verification"]) + "/"
        response = requests.post(url, headers=self.headers, json={"id": id, "verification": verification})
        assert response.status_code == 200, f"Couldn't set verification. {response.status_code}"
