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
import abc


class BaseTable(abc.ABC):
    """
    Interface for CIM report.
    """

    @abc.abstractmethod
    def __init__(self, table_title, header_list):
        pass

    @abc.abstractmethod
    def set_description(self, string):
        raise NotImplementedError()

    @abc.abstractmethod
    def add_row(self, string):
        raise NotImplementedError()

    @abc.abstractmethod
    def set_note(self, string):
        raise NotImplementedError()

    @abc.abstractmethod
    def return_table_str(self):
        raise NotImplementedError()
