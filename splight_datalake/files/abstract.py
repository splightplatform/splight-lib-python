from abc import ABCMeta, abstractmethod


class AbstractFileManager(metaclass=ABCMeta):

    file_repo = ''

    def __init__(self, file_repo):
        self.file_repo = file_repo

    @abstractmethod
    def retrieve_file(self, file_name, path):
        pass

    @abstractmethod
    def upload_file(self, filepath):
        pass
