#
# Copyright 2021 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
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
