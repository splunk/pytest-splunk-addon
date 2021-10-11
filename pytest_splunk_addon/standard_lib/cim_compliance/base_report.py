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


class CIMReport(abc.ABC):
    """
    Interface for CIM report.
    """

    @abc.abstractmethod
    def set_title(self, string):
        raise NotImplementedError()

    @abc.abstractmethod
    def add_section_title(self, string):
        raise NotImplementedError()

    @abc.abstractmethod
    def add_section_description(self, string):
        raise NotImplementedError()

    @abc.abstractmethod
    def add_section_note(self, string):
        raise NotImplementedError()

    @abc.abstractmethod
    def add_table(self, string):
        raise NotImplementedError()

    @abc.abstractmethod
    def write(self, path):
        raise NotImplementedError()
