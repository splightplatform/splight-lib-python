import boto3
from pydantic import BaseModel
from typing import Optional, Type, List

from splight_storage.models import StorageFile
from .abstract import AbstractStorageClient


class S3StorageClient(AbstractStorageClient):

    def save(self, instance: BaseModel) -> BaseModel:
        if isinstance(instance, StorageFile):
            s3 = boto3.client('s3')
            s3.upload_file(f"{instance.file}", self.namespace, instance.name)
            instance.id = "TODO_FIX_THIS"
            return instance
        raise NotImplementedError

    def get(self, resource_type: Type, resource_id: Optional[str] = None) -> List[BaseModel]:
        if resource_type == StorageFile:
            s3 = boto3.client('s3')
            result = [StorageFile(file=obj['Key'], id=obj['ETag'].strip('"')) for obj in s3.list_objects(Bucket=self.namespace)['Contents']]
            if resource_id:
                result = [r for r in result if r.id == resource_id]
            return result
        raise NotImplementedError

    def download(self):
        raise NotImplementedError
        path = f"/tmp/myfile"
        s3 = boto3.client('s3')
        s3.download_file(Bucket=self.namespace, Key=id, Filename=path)
        return path

    def delete(self, resource_type: Type, resource_id: str) -> List[BaseModel]:
        if resource_type == StorageFile:
            s3 = boto3.client('s3')
            s3.delete_object(Bucket=self.namespace, Key=resource_id)
        raise NotImplementedError
