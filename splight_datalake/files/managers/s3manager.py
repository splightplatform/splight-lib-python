import boto3
from .abstract_manager import AbstractFileManager


class S3Manager(AbstractFileManager):

    def __init__(self, *args, **kwargs):
        super(S3Manager, self).__init__(*args, **kwargs)

    def retrieve_file(self, file_name=None, path=None):
        if file_name is None:
            return
        if path is None:
            path = f"/tmp/{file_name}"

        s3 = boto3.client('s3')
        s3.download_file(Bucket=self.file_repo, Key=file_name, Filename=path)
        return path

    def upload_file(self, filepath):
        s3 = boto3.client('s3')
        target_file_name = filepath.split('/')[-1]
        s3.upload_file(f"{filepath}", self.file_repo, target_file_name)
