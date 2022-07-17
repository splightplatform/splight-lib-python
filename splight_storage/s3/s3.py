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

    def __init__(self, namespace="default", bucket=AWS_STORAGE_BUCKET_NAME, *args, **kwargs) -> None:
        super(S3StorageClient, self).__init__(namespace, *args, **kwargs)
        self.s3_resource = self._get_s3_resource()
        self.s3_client = self._get_s3_client()
        self.bucket = bucket

    def _get_s3_client(self):
        return boto3.client("s3",
                            aws_access_key_id=AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                            region_name=AWS_REGION)

    def _get_s3_resource(self):
        return boto3.resource("s3",
                              aws_access_key_id=AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                              region_name=AWS_REGION)

    def _encode_name(self, name):
        name = name.replace(f"{self.namespace}/", '')
        return b64e(zlib.compress(name.encode('utf-8'), 9))

    def _decode_name(self, name):
        decoded_name = zlib.decompress(b64d(name)).decode('utf-8')
        return f"{self.namespace}/{decoded_name}"

    def _namespaced_key(self, name):
        if not name.startswith(self.namespace):
            name = f"{self.namespace}/{name}"
        return name

    def list_files(self, prefix=''):
        prefix = self._namespaced_key(prefix)
        return self.s3_resource.Bucket(self.bucket).objects.filter(Prefix=prefix, Delimiter="/")

    def copy(self, old_name: str, new_name: str):
        old_name, new_name = self._namespaced_key(old_name), self._namespaced_key(new_name)
        copy_source = {
            'Bucket': self.bucket,
            'Key': old_name
        }
        return self.s3_resource.Object(self.bucket, new_name).copy_from(CopySource=copy_source)

    def move(self, old_name: str, new_name: str):
        old_name, new_name = self._namespaced_key(old_name), self._namespaced_key(new_name)
        self.copy(old_name, new_name)
        self.delete(old_name)

    @validate_instance_type
    def save(self, instance: BaseModel, prefix: Optional[str] = None) -> BaseModel:
        keys = [self.namespace, prefix] if prefix else [self.namespace]
        keys.append(instance.name)
        key = '/'.join(keys)
        self.s3_client.upload_file(
            Filename=instance.file,
            Bucket=self.bucket,
            Key=key,
            ExtraArgs={
                'ContentType': instance.content_type
            }
        )
        instance.id = self._encode_name(key)
        return instance

    @validate_resource_type
    def get(self, resource_type: Type, first=False, prefix: Optional[str]=None, **kwargs) -> List[BaseModel]:
        prefixes = [self.namespace, prefix] if prefix else [self.namespace]
        prefix = '/'.join(prefixes)
        files = self.s3_client.list_objects(
            Bucket=self.bucket,
            Prefix=prefix
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
    def delete(self, resource_type: Type, id: str) -> None:
        id = self._namespaced_key(self._decode_name(id))
        self.s3_client.delete_object(
            Bucket=self.bucket,
            Key=id
        )

    @validate_resource_type
    def download(self, resource_type: Type, id: str, target: str) -> str:
        id = self._namespaced_key(self._decode_name(id))
        self.s3_client.download_file(
            Bucket=self.bucket,
            Key=id,
            Filename=target
        )
        return target
    
    @validate_instance_type
    def get_temporary_link(self, instance: BaseModel) -> str:
        key = self._namespaced_key(instance.file)
        url = self.s3_client.generate_presigned_url(
            'get_object',
            Params= {
                'Bucket': self.bucket,
                'Key': key,
            },
            ExpiresIn=3600
        )
        return url
