from abc import abstractmethod

from pytest_splunk_addon.helmut.manager import Manager
from pytest_splunk_addon.helmut.misc.collection import Collection
from pytest_splunk_addon.helmut.misc.manager_utils import (
    create_wrapper_from_connector_mapping,
)


class SavedSearches(Manager, Collection):
    def __init__(self, connector):
        """
        Constructor for SavedSearches.

        @param connector: The connector through which Splunk is reached.
        @type connector: Connector
        """
        Manager.__init__(self, connector)
        Collection.__init__(self)

    def __new__(cls, connector):
        """
        The function called when creating a new SavedSearches object.
        An internal map stores mappings from connector type to corresponding
        SavedSearches subclass, making sure that the appropriate SavedSearches class is
        evoked.

        @param connector: The connector through which Splunk is reached.
        @type connector: Connector
        """
        mappings = _CONNECTOR_TO_WRAPPER_MAPPINGS
        return create_wrapper_from_connector_mapping(cls, connector, mappings)

    @abstractmethod
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
        pass

    @abstractmethod
    def __getitem__(self, saved_search_name):
        """
        Retrieve a saved search.

        @param saved_searc_name: The name of the saved search.
        @type saved_search_name: SavedSearch
        """
        pass


class SavedSearchNotFound(RuntimeError):
    def __init__(self, saved_search_name):
        self.saved_search_name = saved_search_name
        super(SavedSearchNotFound, self).__init__(self._error_message)

    @property
    def _error_message(self):
        f = "Could not find saved search with name {name}"
        return f.format(name=self.saved_search_name)


# We need to do this at the bottom to avoid import errors
from pytest_splunk_addon.helmut.connector.sdk import SDKConnector
from pytest_splunk_addon.helmut.manager.saved_searches.sdk import (
    SDKSavedSearchesWrapper,
)

_CONNECTOR_TO_WRAPPER_MAPPINGS = {SDKConnector: SDKSavedSearchesWrapper}
