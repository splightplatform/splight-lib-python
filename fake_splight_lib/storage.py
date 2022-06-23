import random
import os
from pydantic import BaseModel
from typing import Type, List, Dict
from collections import defaultdict
from splight_lib import logging
from splight_models.storage import StorageFile
from splight_storage.abstract import AbstractStorageClient
from splight_lib.settings import SPLIGHT_HOME


STORAGE_HOME = os.path.join(SPLIGHT_HOME, "storage")
logger = logging.getLogger()


class FakeStorageClient(AbstractStorageClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        os.makedirs(STORAGE_HOME, exist_ok=True)
        os.makedirs(os.path.join(STORAGE_HOME, self.namespace), exist_ok=True)

    def save(self, instance: BaseModel) -> BaseModel:
        logger.debug(f"[FAKED] created file {instance}")
        id = os.path.split(instance.file)[-1]
        destination = os.path.join(STORAGE_HOME, self.namespace, id)
        os.system(f'cp {instance.file} {destination}')
        instance.id = id
        return instance

    def get(self, resource_type: Type, first=False, **kwargs) -> List[BaseModel]:
        logger.debug(f"[FAKED] Getting files {kwargs}")
        queryset = [StorageFile(id=f, file=f) for f in os.listdir(os.path.join(STORAGE_HOME, self.namespace))]
        kwargs = self._validated_kwargs(resource_type, **kwargs)
        queryset = self._filter(queryset, **kwargs)
        if first:
            return queryset[0] if queryset else None
        return queryset

    def delete(self, resource_type: Type, id: str) -> List[BaseModel]:
        logger.debug(f"[FAKED] Deleted file {id}")
        os.remove(os.path.join(STORAGE_HOME, self.namespace, id))

    def download(self, resource_type: Type, id: str, target: str) -> str:
        logger.debug(f"[FAKED] Downloading file {id} to {target}")
        os.system(f'cp {os.path.join(STORAGE_HOME, self.namespace, id)} {target}')
        return target

    def upload(self, id: str):
        raise NotImplementedError

    def get_temporary_link(self, instance: BaseModel) -> str:
        raise NotImplementedError