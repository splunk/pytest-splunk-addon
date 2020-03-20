from pytest_splunk_addon.helmut.log import Logging


class BaseFileUtils(Logging):
    def isfile(self, path):
        raise NotImplementedError("Function not implemented")

    def isdir(self, path):
        raise NotImplementedError("Function not implemented")

    def delete_file(self, file):
        raise NotImplementedError("Function not implemented")

    def get_file_contents(self, path):
        raise NotImplementedError("Function not implemented")

    def write_file_contents(self, path, contents, mode="w"):
        raise NotImplementedError("Function not implemented")

    def copy_file(self, source, target):
        raise NotImplementedError("Function not implemented")

    def move_file(self, source, target):
        raise NotImplementedError("Function not implemented")

    def copy_directory(self, source, target, ignore=None):
        raise NotImplementedError("Function not implemented")

    def compare_files(self, file1, file2):
        raise NotImplementedError("Function not implemented")

    def move_directory(self, source, target, ignore=None):
        raise NotImplementedError("Function not implemented")

    def force_remove_file(self, path):
        raise NotImplementedError("Function not implemented")

    def force_remove_directory(self, path):
        raise NotImplementedError("Function not implemented")

    def force_copy_file(self, source, target):
        raise NotImplementedError("Function not implemented")

    def force_move_file(self, source, target):
        raise NotImplementedError("Function not implemented")

    def force_move_directory(self, source, target):
        raise NotImplementedError("Function not implemented")

    def force_copy_directory(self, source, target):
        raise NotImplementedError("Function not implemented")

    def create_directory(self, path):
        raise NotImplementedError("Function not implemented")
