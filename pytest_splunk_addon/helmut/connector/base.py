"""
Module for handling generic connections with a Splunk instance.

@author: Nicklas Ansman-Giertz
@contact: U{ngiertz@splunk.com<mailto:ngiertz@splunk.com>}
@since: 2011-11-21
"""

from abc import ABCMeta
from builtins import range
from builtins import str

from future.utils import with_metaclass

from pytest_splunk_addon.helmut.log import Logging


class Connector(with_metaclass(ABCMeta, Logging)):
    """
    A connector is an object that handles connections with Splunk.

    This is the abstract base class for all connectors.

    @cvar DEFAULT_USERNAME: The username that will be used if a username is not
                            explicitly specified.
    @cvar DEFAULT_PASSWORD: The password that will be used if a password is not
                            explicitly specified.
    @cvar DEFAULT_OWNER: The owner that will be used if an owner is not
                            explicitly specified.
    @cvar DEFAULT_APP: The app that will be used if an app is not
                            explicitly specified.
    @ivar _splunk: The Splunk instance associated with this connector.
    @ivar _username: The username that this connector uses.
    @ivar _password: The password that this connector uses.
    @ivar _owner: The owner that this connector uses.
    @ivar _app: The app that this connector uses.
    """

    DEFAULT_USERNAME = "admin"
    DEFAULT_PASSWORD = "changeme"
    DEFAULT_OWNER = "nobody"
    DEFAULT_APP = "system"

    # types of connectors
    (SDK, REST) = list(range(0, 2))

    def __init__(self, splunk, username=None, password=None, owner=None, app=None):
        """
        Creates a new Connector instance.

        The namespace needs to be in the <user>:<app> format.

        @param splunk: The Splunk object we are communicating with.
        @type splunk: L{Splunk<..splunk.Splunk>}
        @param username: The username to use (or None for default)
        @type username: str
        @param password: The password to use (or None for default)
        @type password: str
        @param owner: The owner to use (or None for default)
        @type owner: str
        @param app: The app to use (or None for default)
        @type app: str
        """
        self._splunk = splunk
        self._username = username or self.DEFAULT_USERNAME
        self._password = password or self.DEFAULT_PASSWORD
        self._owner = owner or self.DEFAULT_OWNER
        self._app = app or self.DEFAULT_APP
        self._attempt_login_time = 0
        Logging.__init__(self)

    @property
    def splunk(self):
        """
        The Splunk object associated with this connector.

        @rtype: L{Splunk<..splunk.Splunk>}
        """
        return self._splunk

    @property
    def username(self):
        """
        The username for this connector.

        @rtype: str
        """
        return self._username

    @username.setter
    def username(self, value):
        """
        Setter for the username property
        """
        self._username = value

    @property
    def password(self):
        """
        The password for this connector.

        @rtype: str
        """
        return self._password

    @password.setter
    def password(self, value):
        """
        Setter for the password property
        """
        self._password = value

    @property
    def namespace(self):
        """
        The namespace for this connector.

        Will be in the format <owner>:<app>

        @rtype: str
        """
        return str(self._owner) + ":" + str(self._app)

    @property
    def owner(self):
        """
        The owner for this connector.

        @rtype: str
        """
        return self._owner

    @property
    def app(self):
        """
        The app for this connector.

        @rtype: str
        """
        return self._app
