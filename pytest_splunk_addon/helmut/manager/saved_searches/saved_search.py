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
from abc import abstractmethod

from pytest_splunk_addon.helmut.manager.object import ItemFromManager


class SavedSearch(ItemFromManager):
    """
    The SavedSearch class represents an saved search in Splunk.
    """

    @abstractmethod
    def run(self, **kwargs):
        """
        Run this saved search.
        @param **kwargs: Any other settings for running this saved search.
        @type **kwargs: Dictionary
        """
        pass

    @abstractmethod
    def edit(self, query=None, **kwargs):
        """
        Edit this saved search.
        @param query: The query that this saved search is supposed to run.  Remains unchanged if no value is given.
        @type query: String
        @param **kwargs: Any other settings for the saved search.
        @type **kwargs: Dictionary
        """
        pass

    @abstractmethod
    def disable(self):
        """
        Disable this saved search.
        """
        pass

    @abstractmethod
    def enable(self):
        """
        Enable this saved search.
        """
        pass

    @abstractmethod
    def get_artifacts(self):
        """
        Return the artifacts associated with this saved search.

        @return:  A list of the jobs associated with the saved searches.
        @rtype:  list
        """
        pass

    def delete(self):
        """
        Delete this saved search.
        """
        pass
