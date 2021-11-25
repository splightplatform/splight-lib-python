import os
from .managers import managers


class FileManager:

    def __init__(self, *args, **kwargs):
        self.manager = managers[os.getenv('FILE_SOURCE')](*args, **kwargs)

    def retrieve_file(self, file_name=None, path=None):
        filepath = self.manager.retrieve_file(file_name, path)
        return filepath.replace('/', os.sep)

    def upload_file(self, filepath):
        self.manager.upload_file(filepath.replace(os.sep, '/'))
