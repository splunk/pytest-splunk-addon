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
from future.utils import raise_
from splunklib.client import HTTPError

from pytest_splunk_addon.helmut.manager.saved_searches import SavedSearchNotFound
from pytest_splunk_addon.helmut.manager.saved_searches import SavedSearches
from pytest_splunk_addon.helmut.manager.saved_searches.sdk.saved_search import (
    SDKSavedSearchWrapper,
)


class SDKSavedSearchesWrapper(SavedSearches):
    """
    The SavedSearches subclass that wraps the Splunk Python SDK's SavedSearches object.
    It basically contains a collection of L{SDKSavedSearchWrapper}s.
    """

    @property
    def _service(self):
        """
        The service associated with this connector.
        """
        return self.connector.service

    def create(self, saved_search_name, query, **kwargs):
        """
        Create a saved search.

        @param saved_search_name: The name of the new saved search.
        @type saved_search_name: String
        @param query: The actual search to be saved.
        @type query: String
        @param **kwargs: Any other settings for the saved search.
        @type **kwargs: Dictionary
        """
        try:
            self.logger.info("Creating saved search '%s'" % saved_search_name)
            self.connector.service.saved_searches.create(
                saved_search_name, query, **kwargs
            )
        except HTTPError as err:
            # Saved search already exists
            if not err.status == 409:
                raise
            self.logger.warn(
                "Saved search '%s' already exists. HTTPError: %s"
                % (saved_search_name, err)
            )

    def __getitem__(self, saved_search_name):
        """
        Retrieve a saved search.

        @param saved_searc_name: The name of the saved search.
        @type saved_search_name: SavedSearch
        """
        for saved_search in self:
            if saved_search.name == saved_search_name:
                return saved_search
        raise_(SavedSearchNotFound, saved_search_name)

    def __contains__(self, saved_search_name):
        """
        Determines if a saved search with a particular name exists.

        @param key:  The name of the saved search to be found.
        @param type: String
        @return:  Whether or not the saved search exists.
        @rtype:  boolean
        """
        for saved_search in self:
            if saved_search.name == saved_search_name:
                return True
        return False

    def items(self):
        """
        Returns a list of saved searches.

        @return:  A list of saved searches.
        @rtype:  list
        """
        saved_searches = self._service.saved_searches
        return [
            SDKSavedSearchWrapper(self.connector, saved_search)
            for saved_search in saved_searches
        ]
