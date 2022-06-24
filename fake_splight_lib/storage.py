import os
import shutil
import pathlib
from pydantic import BaseModel
from typing import Optional, Type, List
from splight_lib import logging
from splight_models.storage import StorageFile
from splight_storage.abstract import AbstractStorageClient
from splight_lib.settings import SPLIGHT_HOME


STORAGE_HOME = os.path.join(SPLIGHT_HOME, "storage")
logger = logging.getLogger()


class FakeStorageClient(AbstractStorageClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_path = os.path.join(STORAGE_HOME, self.namespace)
        os.makedirs(STORAGE_HOME, exist_ok=True)
        os.makedirs(self.base_path, exist_ok=True)

    def __copy(self, source, destination):
        os.makedirs(os.path.join(*os.path.split(destination)[:-1]), exist_ok=True)
        try:
            shutil.copy(source, destination)
        except shutil.SameFileError:
            logger.exception("Source and destination represents the same file.")
        except PermissionError:
            logger.exception("Permission denied.")
        except:
            logger.exception("Error occurred while copying file.")

    def save(self, instance: BaseModel, prefix: Optional[str] = None) -> BaseModel:
        logger.debug(f"[FAKED] created file {instance}")
        id = os.path.split(instance.file)[-1]
        if prefix:
            if prefix.startswith('/'):
                prefix = pathlib.Path(prefix).relative_to('/')
            id = os.path.join(prefix, id)
        destination = os.path.join(STORAGE_HOME, self.namespace, id)
        self.__copy(instance.file, destination)
        instance.id = id
        return instance

    def get(self, resource_type: Type, first=False, **kwargs) -> List[BaseModel]:
        logger.debug(f"[FAKED] Getting files {kwargs}")
        queryset = []
        for folder, _, files in os.walk(self.base_path):
            for file in files:
                queryset.append(os.path.join(folder, file))
        queryset = [str(pathlib.Path(f).relative_to(self.base_path)) for f in queryset]
        queryset = [StorageFile(id=f, file=f) for f in queryset]
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
        source = os.path.join(STORAGE_HOME, self.namespace, id)
        self.__copy(source, target)
        return target

    def upload(self, id: str):
        raise NotImplementedError

    def get_temporary_link(self, instance: BaseModel) -> str:
        raise NotImplementedError