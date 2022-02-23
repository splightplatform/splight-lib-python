from splight_lib import logging
from splight_storage.abstract import AbstractStorageClient
from pydantic import BaseModel
from typing import Optional, Type, List


logger = logging.getLogger()


class FakeStorageClient(AbstractStorageClient):

    def save(self, instance: BaseModel) -> BaseModel:
        logger.debug(f"[FAKED] created file {instance}")

    def get(self, resource_type: Type, first=False, **kwargs) -> List[BaseModel]:
        logger.debug(f"[FAKED] Geted file {kwargs.get('id')}")

    def delete(self, resource_type: Type, id: str) -> List[BaseModel]:
        logger.debug(f"[FAKED] Deleted file {id}")

    def download(self, resource_type: Type, id: str, target: str) -> str:
        logger.debug(f"[FAKED] Downloading file {id} to {target}")

    def upload(self, id: str):
        logger.debug(f"[FAKED] Uploading file {id}")
