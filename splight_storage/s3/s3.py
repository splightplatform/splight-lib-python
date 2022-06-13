import boto3
import zlib
from pydantic import BaseModel
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d
from typing import Type, List, Optional
from splight_models import StorageFile
from ..abstract import AbstractStorageClient
from .settings import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    AWS_STORAGE_BUCKET_NAME
)
from client import validate_instance_type, validate_resource_type


class S3StorageClient(AbstractStorageClient):
    valid_classes = [StorageFile]

    def __init__(self, *args, **kwargs):
        super(S3StorageClient, self).__init__(*args, **kwargs)
        self.s3 = self._get_s3_client()

    def _get_s3_client(self):
        return boto3.client("s3",
                            aws_access_key_id=AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                            region_name=AWS_REGION)

    def _encode_name(self, name):
        name = name.replace(f"{self.namespace}/", '')
        return b64e(zlib.compress(name.encode('utf-8'), 9))

    def _decode_name(self, name):
        decoded_name = zlib.decompress(b64d(name)).decode('utf-8')
        return f"{self.namespace}/{decoded_name}"

    @validate_instance_type
    def save(self, instance: BaseModel, prefix: Optional[str] = None,) -> BaseModel:

        keys = [self.namespace, prefix] if prefix else [self.namespace]
        keys.append(instance.name)
        key = '/'.join(keys)
        self.s3.upload_file(
            Filename=instance.file,
            Bucket=AWS_STORAGE_BUCKET_NAME,
            Key=key,
            ExtraArgs={
                'ContentType': instance.content_type
            }
        )
        instance.id = self._encode_name(key)
        return instance

    @validate_resource_type
    def get(self, resource_type: Type, first=False, **kwargs) -> List[BaseModel]:
        files = self.s3.list_objects(
            Bucket=AWS_STORAGE_BUCKET_NAME,
            Prefix=self.namespace
        ).get('Contents', [])
        result = [
            StorageFile(file=obj['Key'], id=self._encode_name(obj['Key']))
            for obj in files
        ]

        kwargs = self._validated_kwargs(resource_type, **kwargs)
        result = self._filter(result, **kwargs)
        if first:
            return result[0] if result else None

        return result

    @validate_resource_type
    def download(self, resource_type: Type, id: str, target: str) -> str:
        self.s3.download_file(
            Bucket=AWS_STORAGE_BUCKET_NAME,
            Key=self._decode_name(id),
            Filename=target
        )
        return target
    
    @validate_instance_type
    def get_temporary_link(self, instance: BaseModel) -> str:
        url = self.s3.generate_presigned_url(
            'get_object',
            Params= {
                'Bucket': AWS_STORAGE_BUCKET_NAME,
                'Key': self.namespace + '/' + instance.name,
            },
            ExpiresIn=3600
        )
        return url

    @validate_resource_type
    def delete(self, resource_type: Type, id: str) -> List[BaseModel]:
        self.s3.delete_object(
            Bucket=AWS_STORAGE_BUCKET_NAME,
            Key=self._decode_name(id)
        )
