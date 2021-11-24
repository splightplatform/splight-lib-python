from splight_datalake.managers import managers


class FileManager:

    def __init__(self, manager_str, repo):
        self.manager = managers[manager_str](repo)

    def upload_file(self, file):
        self.manager.upload_file(file)

    def retrieve_file(self, file_name):
        filepath = self.manager.retrieve_file(file_name)
        return filepath
