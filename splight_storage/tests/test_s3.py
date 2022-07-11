import json
from unittest import TestCase
from unittest.mock import patch, Mock
from splight_storage.s3 import S3StorageClient
from splight_models import StorageFile


class TestS3StorageClient(TestCase):
    def setUp(self) -> None:
        self.boto3_client = Mock()
        self.boto3_resource = Mock()
        self.bucket_name = "splight-api"
        with patch("boto3.client", return_value=self.boto3_client):
            with patch("boto3.resource", return_value=self.boto3_resource):
                self.client = S3StorageClient(bucket=self.bucket_name)
        self.instance = StorageFile(
            id='eNorzs9NLcnIzEvXS0xKBgAlhQUj',
            file='something.abc'
        )
        return super().setUp()

    def test_create_file(self):
        with patch.object(self.boto3_client, 'upload_file') as mocked_upload:
            self.client.save(self.instance)
            mocked_upload.assert_called_with(
                Filename='something.abc',
                Bucket=self.bucket_name,
                Key='default/something.abc',
                ExtraArgs={'ContentType': None}
            )

    def test_get_file(self):
        return_value = {
            'Contents': [{
                'Key': 'something.abc',
                'LastModified': None,
                'ETag': '"614bb74e6ea92014d3177473be09b9df"',
                'Size': 5622,
                'StorageClass': 'STANDARD',
                'Owner': None
            }],
            'Name': self.bucket_name,
            'Prefix': 'orgfgmkta1hcu4nwkp1/',
            'MaxKeys': 1000,
            'EncodingType': 'url'
        }
        expected_result = [StorageFile(**self.instance.dict())]
        with patch.object(self.boto3_client, 'list_objects', return_value=return_value) as mocked_list:
            self.assertEqual(self.client.get(resource_type=StorageFile), expected_result)
            mocked_list.assert_called_with(Bucket=self.bucket_name, Prefix='default')

    def test_download_file(self):
        with patch.object(self.boto3_client, 'download_file') as mocked_upload:
            self.client.download(resource_type=StorageFile, id=self.instance.id, target='/tmp/tmp.file')
            mocked_upload.assert_called_with(Bucket=self.bucket_name, Key='default/something.abc', Filename='/tmp/tmp.file')

    def test_delete_file(self):
        with patch.object(self.boto3_client, 'delete_object') as mocked_delete:
            self.client.delete(resource_type=StorageFile, id=self.instance.id)
            mocked_delete.assert_called_with(Bucket=self.bucket_name, Key='default/something.abc')
