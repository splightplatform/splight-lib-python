import os
from splight_datalake.files.managers import managers


class FileManager:

    def __init__(self, *args, **kwargs):
        self.manager = managers[os.getenv('FILE_SOURCE')](*args, **kwargs)

    def retrieve_file(self, file_name, path):
        filepath = self.manager.retrieve_file(file_name, path)
        return filepath

    def upload_file(self, filepath):
        self.manager.upload_file(filepath)
