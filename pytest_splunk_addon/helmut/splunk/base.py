"""
This module has things regarding a generic Splunk instance.

@author: Nicklas Ansman-Giertz
@contact: U{ngiertz@splunk.com<mailto:ngiertz@splunk.com>}
@since: 2011-12-05
"""
import time
from abc import ABCMeta, abstractmethod, abstractproperty

from future.utils import with_metaclass

from pytest_splunk_addon.helmut.connector.base import Connector
from pytest_splunk_addon.helmut.connector.rest import RESTConnector
from pytest_splunk_addon.helmut.connector.sdk import SDKConnector
from pytest_splunk_addon.helmut.exceptions import UnsupportedConnectorError
from pytest_splunk_addon.helmut.exceptions.command_execution import (
    CommandExecutionFailure,
)
from pytest_splunk_addon.helmut.log import Logging
from pytest_splunk_addon.helmut.util.rip import RESTInPeace


class Splunk(with_metaclass(ABCMeta, Logging)):
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
        Connector.REST: RESTConnector,
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
        self.logger.debug("Helmut Splunk created:{splunk}".format(splunk=self))

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

    @abstractproperty
    def _str_format(self):
        """
        The format to use when casting this instance to a string.

        @rtype: str
        """

    @abstractproperty
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

        if contype not in self._CONNECTOR_TYPE_TO_CLASS_MAPPINGS:
            raise UnsupportedConnectorError

        if args:
            self.logger.debug(
                "Args in create_connector is deprecated, Please use kwargs."
            )
        conn = self._CONNECTOR_TYPE_TO_CLASS_MAPPINGS[contype](self, *args, **kwargs)

        connector_id = self._get_connector_id(contype=contype, user=conn.username)

        if connector_id in list(self._connectors.keys()):
            self.logger.warning(
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

        if contype == "REST":
            rest_conn = self.create_logged_in_connector(
                contype=Connector.REST, username=username, password=password
            )
            self._attempt_login(rest_conn)
            return rest_conn

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
        from pytest_splunk_addon.helmut.manager.jobs import Jobs

        return Jobs(self.connector(contype, username))

    def confs(self, contype=None, username=None, password=None):
        """
        Returns a Confs manager that uses the specified connector. Defaults to
        default connector if none specified.

        This property creates a new Confs manager each call so you may do as
        you please with it.

        @param contype: type of connector, defined in L{Connector} class
        @param username: connector's username
        @type username: string
        @rtype: L{Confs}
        """
        from pytest_splunk_addon.helmut.manager.confs import Confs

        return Confs(self.connector(contype, username, password))

    def inputs(self, contype=None, username=None):
        """
        Returns a Inputs manager that uses the specified connector. Defaults to
        default connector if none specified.

        This property creates a new Inputs manager each call so you may do as
        you please with it.

        @param contype: type of connector, defined in L{Connector} class
        @param username: connector's username
        @type username: string
        @rtype: L{Inputs}
        """
        from pytest_splunk_addon.helmut.manager.inputs import Inputs

        return Inputs(self.connector(contype, username))

    def indexes(self, contype=None, username=None, password=None):
        """
        Returns a Indexes manager that uses the specified connector. Defaults
        to default connector if none specified.

        This property creates a new Indexes manager each time it is called so
        you may handle the object as you wish.

        @param contype: type of connector, defined in L{Connector} class
        @param username: connector's username
        @type username: string
        @rtype: L{Indexes}
        """
        from pytest_splunk_addon.helmut.manager.indexes import Indexes

        return Indexes(self.connector(contype, username, password))

    def roles(self, contype=None, username=None):
        """
        Returns a Roles manager that uses the specified connector. Defaults to
        default connector if none specified.

        This property creates a new Roles manager each call so you may do as
        you please with it.

        @param contype: type of connector, defined in L{Connector} class
        @param username: connector's username
        @type username: string
        @rtype: L{Roles}
        """
        from pytest_splunk_addon.helmut.manager.roles import Roles

        return Roles(self.connector(contype, username))

    def saved_searches(self, contype=None, username=None):
        """
        Returns a SavedSearches manager that uses the specified connector.
        Defaults to default connector if none specified.

        This property creates a new SavedSearches manager each
        call so you may do as you please with it.

        @param contype: type of connector, defined in L{Connector} class
        @param username: connector's username
        @type username: string
        @rtype: L{SavedSearch}
        """
        from pytest_splunk_addon.helmut.manager.saved_searches import SavedSearches

        return SavedSearches(self.connector(contype, username))

    def users(self, contype=None, username=None):
        """
        Returns a Users manager that uses the specified connector. Defaults to
        default connector if none specified.

        This property creates a new Users manager each call so you may do as
        you please with it.

        @param contype: type of connector, defined in L{Connector} class
        @param username: connector's username
        @type username: string
        @rtype: L{Users}
        """
        from pytest_splunk_addon.helmut.manager.users import Users

        return Users(self.connector(contype, username))

    def _notify_listeners_of_splunk_start(self):
        """
        Notifies all the listeners that Splunk has started.

        Should be called by subclasses when Splunk has (re)started.
        """
        for l in self._start_listeners:
            l()

    def get_rip(self, owner=None, app=None, username=None, password=None):
        """
        Create a RESTInPeace under certian user and app namespace

        :param owner: owner namespace, default to admin
        :type owner: str
        :param app: app namespace, default to search
        :type app: str
        :param username: default to self.username
        :type username: str
        :param password: default to self.password
        :type password: str
        :return: RESTInPeace
        :rtype: RESTInPeace
        """
        username = username or self.username
        password = password or self.password

        self.create_logged_in_connector(
            contype=Connector.REST,
            username=username,
            password=password,
            owner=owner,
            app=app,
        )
        return RESTInPeace(self.connector(Connector.REST, username))

    # Abstract methods

    @abstractmethod
    def restart(self):
        """
        Restarts the Splunk instance.

        Subclasses should call the L{_notify_listeners_of_splunk_start} method
        when Splunk has restarted.

        @raise CouldNotRestartSplunk: If Splunk could not be restarted
        @rtype: None
        """

        pass

    @abstractmethod
    def is_running(self):
        """
        Checks if Splunk is up and running.

        When this returns False a lot of commands will probably fail.

        @rtype: bool
        @return: True if Splunk is started, False otherwise.
        """
        pass

    @abstractmethod
    def splunkd_scheme(self):
        """
        Returns the scheme for the splunkd instance.

        Should be either C{http} or C{https}

        @return: The scheme
        @rtype: str
        """
        pass

    @abstractmethod
    def get_host_os(self):
        """
        Returns the os of the host.
        """
        pass

    @abstractmethod
    def splunkd_host(self):
        """
        Returns the host for the splunkd instance.

        Should be either a hostname or an IP address

        @return: The host
        @rtype: str
        """
        pass

    @abstractmethod
    def splunkd_port(self):
        """
        Returns the port for the splunkd instanct.

        @return: The port
        @rtype: int
        """
        pass

    def enable_listen(self, ports):
        """
        Enable this Splunk instance to receive data through certain TCP ports.

        Port values which are not ints or within the range 0-65535 will be
        ignored.

        @param ports: The ports through which the data is received.
        @type ports: A list of ints detailing which ports to be enabled.
        """
        pass

    def disable_listen(self, ports):
        """
        Disable ports through which this Splunk instance is receiving data.

        Port values which are not ints or within the range 0-65535 will be
        ignored.

        @param ports: The port through which the data was received.
        @type ports: A list of ints detailing which ports to be disabled.
        """
        pass

    def check_for_fields_in_source(self, source, fieldsList):
        """
        checks if the fields present in the fieldsList are being extracted
         & stored by the splunk. It returns the list of missing fields.
        """
        pass

    def is_monitoring_source(self, source):
        """
        Checks if splunk is already monitoring a given source. If it is
        already, it returns True, otherwise, it returns False
        """
        pass

    def _dump_splunkd_process(self):
        """
        Dump splunkd process/opening port into log for troubleshooting
        """
        pass


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


class CouldNotRestartSplunk(CommandExecutionFailure):
    """
    Raised when a Splunk restart fails.
    """

    pass


class InvalidConnector(KeyError):
    """
    Raised when accessing an invalid connector
    """

    pass
