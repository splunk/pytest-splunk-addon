"""
@author: Nicklas Ansman-Giertz
@contact: U{ngiertz@splunk.com<mailto:ngiertz@splunk.com>}
@since: 2011-11-23
"""
from abc import abstractmethod

from pytest_splunk_addon.helmut.manager import Manager
from pytest_splunk_addon.helmut.misc.collection import Collection
from pytest_splunk_addon.helmut.misc.manager_utils import (
    create_wrapper_from_connector_mapping,
)

PATH_PERFIX = "/servicesNS/nobody/system/data/indexes/"
COUNT_OFFSET = "?count=-1&offset=0"
DISABLE = "/disable"
ENABLE = "/enable"
SYSTEM_MESSAGE = "/servicesNS/nobody/system/messages"
RESTART = "/services/server/control/restart"
ROLL_HOT_BUCKETS = "/roll-hot-buckets"


class Indexes(Manager, Collection):
    """
    This class represents the Indexes endpoint in REST which is a collection of
    L{Index}es.
    """

    def __init__(self, connector):
        """
        Indexes' constructor.

        @param connector: The connector through which Splunk is reached.
        @type connector: Connector
        """
        Manager.__init__(self, connector)
        Collection.__init__(self)

    def __new__(cls, connector):
        """
        The function called when creating a new Indexes object.
        An internal map stores mappings from connector type to corresponding
        Indexes subclass, making sure that the appropriate Indexes class is
        evoked.

        @param connector: The connector through which Splunk is reached.
        @type connector: Connector
        """
        mappings = _CONNECTOR_TO_WRAPPER_MAPPINGS
        return create_wrapper_from_connector_mapping(cls, connector, mappings)

    @abstractmethod
    def create_index(self, index_name):
        """
        Create an index.

        @param index_name: The name of the new index.
        @type index_name: String
        """
        pass

    @abstractmethod
    def __getitem__(self, index_name):
        """
        Retrieve an index.

        @param index_name: Index name.
        @type index_name: L{String}
        """
        pass


class IndexNotFound(RuntimeError):
    def __init__(self, index_name):
        self.index_name = index_name
        super(IndexNotFound, self).__init__(self._error_message)

    @property
    def _error_message(self):
        f = "Could not find index with name {name}"
        return f.format(name=self.index_name)


class OperationError(Exception):
    """Raised for a failed operation, such as a time out."""

    pass


# We need to do this at the bottom to avoid import errors
from pytest_splunk_addon.helmut.connector.sdk import SDKConnector
from pytest_splunk_addon.helmut.connector.rest import RESTConnector
from pytest_splunk_addon.helmut.manager.indexes.sdk import SDKIndexesWrapper
from pytest_splunk_addon.helmut.manager.indexes.rest import RESTIndexesWrapper

_CONNECTOR_TO_WRAPPER_MAPPINGS = {
    SDKConnector: SDKIndexesWrapper,
    RESTConnector: RESTIndexesWrapper,
}
