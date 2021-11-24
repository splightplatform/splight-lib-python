from splight_datalake.managers import managers


class FileManager:

    def __init__(self, args, kwargs):
        manager_str = args[0] if len(args) > 1 else kwargs.pop('manager')
        self.manager = managers[manager_str]()
        super(FileManager, self).__init__(args[1:], kwargs)

    def upload_file(self, file):
        self.manager.upload_file(file)

    def retrieve_file(self, file_name):
        filepath = self.manager.retrieve_file(file_name)
        return filepath
