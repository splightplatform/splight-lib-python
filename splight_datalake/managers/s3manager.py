import boto3
from generic_manager import GenericFileManager


class S3Manager(GenericFileManager):

    def retrieve_file(self, file_name=None, path=None):
        if file_name is None:
            return
        if path is None:
            path = f"/tmp/{file_name}"

        s3 = boto3.client('s3')
        s3.download_file(Bucket=self.file_repo, Key=file_name, Filename=path)
        return path

    def upload_file(self, file):
        s3 = boto3.client('s3')
        target_file_name = file.split('/')[-1]
        s3.upload_file(f"{file}", self.file_repo, target_file_name)
