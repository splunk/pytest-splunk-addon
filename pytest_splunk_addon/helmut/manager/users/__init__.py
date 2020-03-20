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


class Users(Manager, Collection):
    """
    This class represents the Users endpoint in REST which is a collection of
    L{User}es.
    """

    def __init__(self, connector):
        """
        Users' constructor.

        @param connector: The connector through which Splunk is reached.
        @type connector: Connector
        """
        Manager.__init__(self, connector)
        Collection.__init__(self)

    def __new__(cls, connector):
        """
        The function called when creating a new Users object.
        An internal map stores mappings from connector type to corresponding
        Users subclass, making sure that the appropriate Users class is
        evoked.

        @param connector: The connector through which Splunk is reached.
        @type connector: Connector
        """
        mappings = _CONNECTOR_TO_WRAPPER_MAPPINGS
        return create_wrapper_from_connector_mapping(cls, connector, mappings)

    @abstractmethod
    def create_user(self, username, password, roles, **kwargs):
        """
        Create an user.

        @param username: The name of the new user.
        @type username: String
        @param password: The password of the new user.
        @type password: String
        @param roles: The role(s) of the new user.
        @type roles: String or list
        @param kwargs: The arugments the new user.
        @type kwargs: kwargs
        """
        pass

    @abstractmethod
    def delete_user(self, username):
        """
        Delete an user.

        @param username: The name of the user to be deleted.
        @type username: String
        """
        pass

    @abstractmethod
    def __getitem__(self, username):
        """
        Retrieve an user.

        @param username: User's name.
        @type username: L{User}
        """
        pass


class UserNotFound(RuntimeError):
    def __init__(self, user_name):
        self.user_name = user_name
        super(UserNotFound, self).__init__(self._error_message)

    @property
    def _error_message(self):
        f = "Could not find user with name {name}"
        return f.format(name=self.user_name)


# We need to do this at the bottom to avoid import errors
from pytest_splunk_addon.helmut.connector.sdk import SDKConnector
from pytest_splunk_addon.helmut.manager.users.sdk import SDKUsersWrapper

_CONNECTOR_TO_WRAPPER_MAPPINGS = {SDKConnector: SDKUsersWrapper}
