from pydantic import BaseModel
import random
from typing import Type, List, Dict
from collections import defaultdict
from splight_lib import logging
from splight_storage.abstract import AbstractStorageClient


logger = logging.getLogger()


class FakeStorageClient(AbstractStorageClient):
    database: Dict[Type, List[BaseModel]] = defaultdict(list)

    def save(self, instance: BaseModel) -> BaseModel:
        logger.debug(f"[FAKED] created file {instance}")
        instance.id = str(random.randint(1, 1000))
        self.database[type(instance)].append(instance)
        return instance

    def get(self, resource_type: Type, first=False, **kwargs) -> List[BaseModel]:
        logger.debug(f"[FAKED] Getting files {kwargs}")
        queryset = self.database[resource_type]
        kwargs = self._validated_kwargs(resource_type, **kwargs)
        queryset = self._filter(queryset, **kwargs)
        if first:
            return queryset[0] if queryset else None
        return queryset

    def delete(self, resource_type: Type, id: str) -> List[BaseModel]:
        logger.debug(f"[FAKED] Deleted file {id}")
        queryset = self.database.get(resource_type, [])
        for i, item in enumerate(queryset):
            if item.id == id:
                del queryset[i]
                return

    def download(self, resource_type: Type, id: str, target: str) -> str:
        logger.debug(f"[FAKED] Downloading file {id} to {target}")
        with open(target, "w+") as f:
            f.write("FAKED DOWNLOADED FILE CONTENT")
        return target

    def upload(self, id: str):
        logger.debug(f"[FAKED] Uploading file {id}")
