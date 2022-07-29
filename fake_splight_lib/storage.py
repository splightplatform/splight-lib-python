import os
import shutil
import pathlib
import zlib
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d
from pydantic import BaseModel
from typing import Optional, Type, List
from splight_lib import logging
from splight_models.storage import StorageFile
from splight_abstract import AbstractStorageClient
from splight_lib.settings import SPLIGHT_HOME


STORAGE_HOME = os.path.join(SPLIGHT_HOME, "storage")
logger = logging.getLogger()


class FakeStorageClient(AbstractStorageClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_path = os.path.join(STORAGE_HOME, self.namespace)
        os.makedirs(STORAGE_HOME, exist_ok=True)
        os.makedirs(self.base_path, exist_ok=True)

    def _encode_name(self, name):
        name = name.replace(f"{self.namespace}/", '')
        return b"fake" + b64e(zlib.compress(name.encode('utf-8'), 9))

    def _decode_name(self, name):
        name = name.replace("fake", "")
        decoded_name = zlib.decompress(b64d(name)).decode('utf-8')
        return f"{self.namespace}/{decoded_name}"

    def _namespaced_key(self, name):
        if not name.startswith(self.namespace):
            name = f"{self.namespace}/{name}"
        return name

    def copy(self, old_name, new_name):
        new_name_path = os.path.split(new_name)
        if new_name_path[0] != "":
            os.makedirs(os.path.join(*new_name_path[:-1]), exist_ok=True)
        try:
            shutil.copy(old_name, new_name)
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
        self.copy(instance.file, destination)
        id = self._encode_name(id)
        instance.id = id
        return instance

    def _get(self,
             resource_type: Type,
             first=False,
             limit_: int = -1,
             skip_: int = 0,
             prefix: Optional[str] = None,
             **kwargs) -> List[BaseModel]:
        logger.debug(f"[FAKED] Getting files {kwargs}")
        base_path = self.base_path + "/" + prefix if prefix else self.base_path
        queryset = []
        if os.path.isfile(base_path):
            relative_path = str(pathlib.Path(base_path).relative_to(self.base_path))
            queryset = [StorageFile(id=self._encode_name(relative_path), file=relative_path)]
        else:
            for folder, _, files in os.walk(base_path):
                for file in files:
                    queryset.append(os.path.join(folder, file))
            queryset = [str(pathlib.Path(f).relative_to(self.base_path)) for f in queryset]
            queryset = [StorageFile(id=self._encode_name(f), file=f) for f in queryset]
        kwargs = self._validated_kwargs(resource_type, **kwargs)
        queryset = self._filter(queryset, **kwargs)
        if limit_ != -1:
            queryset = queryset[skip_:skip_ + limit_]

        if first:
            return queryset[0] if queryset else None
        return queryset

    def delete(self, resource_type: Type, id: str) -> List[BaseModel]:
        logger.debug(f"[FAKED] Deleted file {id}")
        id = self._namespaced_key(self._decode_name(id))
        os.remove(os.path.join(STORAGE_HOME, id))

    def download(self, resource_type: Type, id: str, target: str) -> str:
        logger.debug(f"[FAKED] Downloading file {id} to {target}")
        id = self._namespaced_key(self._decode_name(id))
        source = os.path.join(STORAGE_HOME, id)
        self.copy(source, target)
        return target

    def upload(self, id: str):
        raise NotImplementedError

    def get_temporary_link(self, instance: BaseModel) -> str:
        raise NotImplementedError
