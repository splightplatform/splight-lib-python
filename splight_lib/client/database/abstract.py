from abc import abstractmethod
from tempfile import NamedTemporaryFile
from typing import Dict, List, Union

from splight_lib.abstract.client import AbstractClient, QuerySet


class AbstractDatabaseClient(AbstractClient):
    @abstractmethod
    def save(self, resource_name: str, instance: Dict) -> Dict:
        pass

    @abstractmethod
    def _get(
        self, resource_name: str, first: bool = False, **kwargs
    ) -> Union[Dict, List[Dict]]:
        pass

    def get(self, resource_name: str, *args, **kwargs) -> QuerySet:
        return QuerySet(self, resource_name, *args, **kwargs)

    @abstractmethod
    def delete(self, resource_name: str, id: str) -> None:
        pass

    @abstractmethod
    def download(self, instance: Dict) -> NamedTemporaryFile:
        pass
