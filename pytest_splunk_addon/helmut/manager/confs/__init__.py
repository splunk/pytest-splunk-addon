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

PATH_CONF = "configs/conf-%s/"
PATH_PROPERTIES = "properties/"
PATH_PERFIX = "/servicesNS/nobody/system/"
COUNT_OFFSET = "?count=-1&offset=0"


class Confs(Manager, Collection):
    """
    This manager represents the collection of .conf files of the Splunk system.

    A notable difference to most other managers is that there are two layers
    of ItemFromManager classes in this class:

    * Confs contains all the .conf files represented as Conf objects (which are
    of the type ItemFromManager).
    * A Conf object contains all the stanzas represented as Stanza objects
    (which are also of the type ItemFromManager).
    * A Stanza contains a collection of key-value pairs corresponding to the
    content of a stanza.
    """

    def __init__(self, connector):
        """
        The constructor of Confs.

        @param connector: The connector through which Splunk is reached.
        @type connector: Connector
        """
        Manager.__init__(self, connector)
        Collection.__init__(self)

    def __new__(cls, connector):
        """
        The function called when creating a new Confs object.
        An internal map stores mappings from connector type to corresponding
        Indexes subclass, making sure that the appropriate Indexes class is
        evoked.

        @param connector: The connector through which Splunk is reached.
        @type connector: Connector
        """
        mappings = _CONNECTOR_TO_WRAPPER_MAPPINGS
        return create_wrapper_from_connector_mapping(cls, connector, mappings)

    @abstractmethod
    def __getitem__(self, conf_name):
        """
        Fetch a .conf file.

        @param conf_name: The name of the conf file to fetch.
        @type conf_name: String
        """
        pass

    def __contains__(self, conf_name):
        for conf in self:
            if conf.name == conf_name:
                return True
        return False

    @abstractmethod
    def create(self, conf_name):
        """
        Create a new .conf file. If .conf file already exists do nothing
        except returning the .conf file.

        @param conf_name: The name of the .conf file to create.
        @type conf_name: String.
        """
        pass


# We need to do this at the bottom to avoid import errors
from pytest_splunk_addon.helmut.connector.sdk import SDKConnector
from pytest_splunk_addon.helmut.connector.rest import RESTConnector
from pytest_splunk_addon.helmut.manager.confs.sdk import SDKConfsWrapper
from pytest_splunk_addon.helmut.manager.confs.rest import RESTConfsWrapper

_CONNECTOR_TO_WRAPPER_MAPPINGS = {
    SDKConnector: SDKConfsWrapper,
    RESTConnector: RESTConfsWrapper,
}
