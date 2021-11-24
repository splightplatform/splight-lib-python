from splight_datalake.managers import managers


class FileManager:

    def __init__(self, manager_str, repo):
        self.manager = managers[manager_str](repo)

    def retrieve_file(self, file_name, path):
        filepath = self.manager.retrieve_file(file_name, path)
        return filepath

    def upload_file(self, filepath):
        self.manager.upload_file(filepath)
