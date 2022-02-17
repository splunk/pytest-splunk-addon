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
"""
This module has things regarding a generic Splunk instance.

@author: Nicklas Ansman-Giertz
@contact: U{ngiertz@splunk.com<mailto:ngiertz@splunk.com>}
@since: 2011-12-05
"""
import logging
import time

from pytest_splunk_addon.helmut.connector.base import Connector
from pytest_splunk_addon.helmut.connector.sdk import SDKConnector

LOGGER = logging.getLogger("helmut")


class Splunk:
    """
    Represents a Splunk instance.

    The Splunk instance may be on the same machine or a remote one.

    This class is abstract and cannot be instantiated directly.

    @ivar connector_factory: The factory to use when creating the connector.
    @type connector_factory: function
    @ivar _default_connector: The default connector. Is None at first and is
                              later created when L{default_connector} is used.
    @type _default_connector: L{Connector}
    @ivar _start_listeners: A collection of start listeners
    @type _start_listeners: set
    @ivar name: The name of this instance. Defaults to the ID of this object.
    @type name: str
    @ivar _logger: The logger this instance uses.
    """

    _username = "admin"
    _password = "changeme"

    _CONNECTOR_TYPE_TO_CLASS_MAPPINGS = {
        Connector.SDK: SDKConnector,
    }
    _is_an_universal_forwarder = False

    def __init__(self, name):
        """
        Creates a new Splunk instance.
        """
        self._default_connector = None
        self._start_listeners = set()
        self._connectors = {}

        self._name = name or id(self)
        super(Splunk, self).__init__()
        LOGGER.debug("Helmut Splunk created:{splunk}".format(splunk=self))

    def __str__(self):
        """
        Casts this instance to a string.

        @return: The string representation of this object.
        @rtype: str
        """
        return self._str_format.format(**self._str_format_arguments)

    @property
    def _logger_name(self):
        """
        :return: constructed logger name as {cls}({name})
        """
        return "{cls}({name})".format(cls=self.__class__.__name__, name=self.name)

    def _str_format(self):
        """
        The format to use when casting this instance to a string.

        @rtype: str
        """

    def _str_format_arguments(self):
        """
        The arguments for the L{_str_format} to use when casting this instance
        to a string.

        @rtype: dict
        """

    @property
    def name(self):
        """
        The name of this instance.

        @rtype: str
        """
        return self._name

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    def register_start_listener(self, listener):
        """
        Adds a listener that will be notified when splunk (re)starts.

        This can be used to re-read values from conf files or recreate things
        that become invalid when Splunk restarts such as auth tokens.

        The listener must be a function (respond to C{__call__} to be more
        precise)

        @param listener: The start listener
        @raise InvalidStartListener: If the listener is not callable.
        """
        _validate_start_listener(listener)
        self._start_listeners.add(listener)

    def unregister_start_listener(self, listener):
        """
        Removes the specified start listener.

        If the listener is not in the list this call has no effect.

        @param listener: The listener to remove
        """
        try:
            self._start_listeners.remove(listener)
        except KeyError:
            pass

    def create_connector(
        self, contype=None, username=None, password=None, *args, **kwargs
    ):
        """
        Creates and returns a new connector of the type specified or
        SDK connector if none specified

        This connector will not be logged in, for that see
        L{create_logged_in_connector}

        Any argument specified to this method will be passed to the connector's
        initialization method

        @param contype: Type of connector to create, defined in Connector
                        class, defaults to Connector.SDK

        @param args: Deprecated.
        @param kwargs: owner, app, sharing(for SDK connector)

        @return: The newly created connector
        """
        contype = contype or Connector.SDK
        kwargs["username"] = username or self.username
        kwargs["password"] = password or self.password

        if args:
            LOGGER.debug(
                "Args in create_connector is deprecated, Please use kwargs."
            )
        conn = self._CONNECTOR_TYPE_TO_CLASS_MAPPINGS[contype](self, *args, **kwargs)

        connector_id = self._get_connector_id(contype=contype, user=conn.username)

        if connector_id in list(self._connectors.keys()):
            LOGGER.warning(
                "Connector {id} is being replaced".format(id=connector_id)
            )
            del self._connectors[connector_id]
        self._connectors[connector_id] = conn

        return self._connectors[connector_id]

    def create_logged_in_connector(
        self,
        set_as_default=False,
        contype=None,
        username=None,
        password=None,
        *args,
        **kwargs
    ):
        """
        Creates and returns a new connector of type specified or of type
        L{SDKConnector} if none specified.

        This method is identical to the L{create_connector} except that this
        method also logs the connector in.

        Any argument specified to this method will be passed to the connector's
        initialization method

        @param set_as_default: Determines whether the created connector is set
                               as the default connector too. True as default.
        @type bool
        @param contype: type of connector to create, available types defined in
            L{Connector} class. Connector.SDK as default

        @return: The newly created, logged in, connector
        """
        contype = contype or Connector.SDK
        conn = self.create_connector(
            contype, username=username, password=password, *args, **kwargs
        )
        if set_as_default:
            self._default_connector = conn
        conn.login()
        return conn

    def set_default_connector(self, contype, username):
        """
        Sets the default connector to an already existing connector

        @param contype: type of connector, defined in L{Connector} class
        @param username: splunk username used by connector
        @type username: string
        """
        self._default_connector = self.connector(contype, username)

    def remove_connector(self, contype, username):
        """
        removes a  connector, sets default connector to None if removing the
        default connector

        @param contype: type of connector, defined in L{Connector} class
        @param username: splunk username used by connector
        @type username: string
        """
        if self.default_connector == self.connector(contype, username):
            self._default_connector = None

        connector_id = self._get_connector_id(contype, username)
        del self._connectors[connector_id]

    def _get_connector_id(self, contype, user):
        """
        Returns the connector id

        @param contype: type of connector, defined in L{Connector} class
        @param username: splunk username used by connector
        @type username: string
        """
        connector_id = "{contype}:{user}".format(contype=contype, user=user)
        return connector_id

    def set_credentials_to_use(self, username="admin", password="changeme"):
        """
        This method just initializes/updates self._username to username
        specified & self._password to password specified

        @param username: splunk username that gets assigned to _username
                         property of splunk class

        @param password: splunk password for the above username.
        Note: This method won't create/update the actual credentials on
              the splunk running instance.

        It is asssumed that credentials specified here are already
        valid credentials.
        """
        self._username = username
        self._password = password

    @property
    def default_connector(self):
        """
        Returns the default connector for this Splunk instance.

        This method caches the value so it isn't created on every call.
        """
        if self._default_connector is None:
            self._default_connector = self.create_logged_in_connector(
                set_as_default=True, username=self.username, password=self.password
            )
        self._attempt_login(self._default_connector)
        return self._default_connector

    @classmethod
    def _attempt_login(cls, connector):
        if (
            hasattr(connector, "is_logged_in")
            and connector._attempt_login_time > 0
            and time.time() - connector._attempt_login_time > 30 * 60
            and not connector.is_logged_in()
        ):
            connector.login()

    def connector(self, contype=None, username=None, password=None):
        """
        Returns the connector specified by type and username, defaults to
        the default connector if none specified

        @param contype: type of connector, defined in L{Connector} class
        @param username: connector's username
        @type username: string
        """
        if contype is None and username is None:
            return self.default_connector

        connector_id = self._get_connector_id(contype, username)
        if connector_id not in list(self._connectors.keys()):
            raise InvalidConnector(
                "Connector {id} does not exist".format(id=connector_id)
            )
        connector = self._connectors[connector_id]
        self._attempt_login(connector)
        return connector

    def jobs(self, contype=None, username=None):
        """
        Returns a Jobs manager that uses the specified connector. Defaults to
        default connector if none specified.

        This property creates a new Jobs manager each call so you may do as
        you please with it.

        @param contype: type of connector, defined in L{Connector} class
        @param username: connector's username
        @type username: string
        @rtype: L{Jobs}
        """
        from pytest_splunk_addon.helmut.manager.jobs.sdk import SDKJobsWrapper

        return SDKJobsWrapper(self.connector(contype, username))

    def _notify_listeners_of_splunk_start(self):
        """
        Notifies all the listeners that Splunk has started.

        Should be called by subclasses when Splunk has (re)started.
        """
        for l in self._start_listeners:
            l()


def _validate_start_listener(listener):
    """
    Validates the start listener making sure it can be called.

    @param listener: The start listener
    @raise InvalidStartListener: If the listener is invalid
    """
    if not _variable_is_a_function(listener):
        raise InvalidStartListener


def _variable_is_a_function(variable):
    """
    Checks if a specified variable is a function by checking if it implements
    the __call__ method.

    This means that the object doesn't have to be a function to pass this
    function, just implement __call__

    @return: True if the variable is a function
    @rtype: bool
    """
    return hasattr(variable, "__call__")


class InvalidStartListener(AttributeError):
    """
    Exception for when the start listener does not implement the
    splunk_has_started method
    """

    def __init__(self, message=None):
        message = message or "Start listeners must be callable"
        super(InvalidStartListener, self).__init__(message)


class InvalidConnector(KeyError):
    """
    Raised when accessing an invalid connector
    """

    pass
