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
import logging
import sys
import time

from splunklib.binding import HTTPError

from pytest_splunk_addon.helmut.manager.jobs.sdk import SDKJobsWrapper
from pytest_splunk_addon.helmut.connector.sdk import SDKConnector

LOGGER = logging.getLogger("helmut")


class CloudSplunk:

    _username = "admin"
    _password = "changeme"

    def __init__(
        self,
        name=None,
        splunkd_scheme=None,
        splunkd_host=None,
        splunkd_port="",
        web_scheme=None,
        web_host=None,
        web_port=None,
        username="admin",
        password="changeme",
    ):
        """
        Creates a new CloudSplunk instance.

        About web url:
         If web_scheme, web_host are given, use them.
         If not, will try to query /services/server/settings to find web info.
         If no sufficient permissions to query, will set it to default http://{_splunkd_host}:{}
        """

        self._splunkd_scheme = splunkd_scheme or "https"
        self._splunkd_port = splunkd_port or "8089"
        self._splunkd_host = splunkd_host or "127.0.0.1"
        self._default_connector = None
        self._start_listeners = set()
        self._connectors = {}
        self._name = name or id(self)
        LOGGER.debug(f"Helmut Splunk created:{self}")
        self.set_credentials_to_use(username=username, password=password)

        server_web_scheme = server_web_host = server_web_port = None
        if not (web_scheme and web_host):
            try:
                sdkconn = self.create_logged_in_connector()
                server_settings = sdkconn.service.settings
                server_web_scheme = (
                    "http" if server_settings["enableSplunkWebSSL"] == "0" else "https"
                )
                server_web_host = server_settings["host"]
                server_web_port = server_settings["httpport"]
                self._pass4SymmKey = server_settings["pass4SymmKey"]
            except HTTPError:
                LOGGER.warning("No sufficient permissions to query server settings.")
        self._web_scheme = web_scheme or server_web_scheme or "http"
        self._web_host = web_host or server_web_host or self._splunkd_host
        self._web_port = web_port or server_web_port or ""
        LOGGER.debug(f"Set web base to: {self.web_base()}")

    @property
    def _str_format(self):
        return '<{cls}@{id} name="{name}" uri="{uri_base}>'

    @property
    def _str_format_arguments(self):
        return {
            "cls": self.__class__.__name__,
            "id": id(self),
            "name": self.name,
            "uri_base": self.uri_base(),
        }

    def __str__(self):
        return self._str_format.format(**self._str_format_arguments)

    @property
    def name(self):
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

    def splunkd_scheme(self):
        return self._splunkd_scheme

    def splunkd_host(self):
        return self._splunkd_host

    def splunkd_port(self):
        return self._splunkd_port

    def uri_base(self):
        """
        Returns the splunkd host.

        @return: The host.
        @rtype: str
        """
        return (
            self.splunkd_scheme()
            + "://"
            + self.splunkd_host()
            + ":"
            + str(self.splunkd_port())
        )

    @property
    def pass4SymmKey(self):
        if not self._pass4SymmKey:
            sdkconn = self.create_logged_in_connector()
            server_settings = sdkconn.service.settings
            self._pass4SymmKey = server_settings["pass4SymmKey"]
        return self._pass4SymmKey

    def web_scheme(self):
        return self._web_scheme

    def web_host(self):
        return self._web_host

    def web_port(self):
        if self._web_port:
            return self._web_port

    def web_base(self):
        """
        Returns the splunk web server.

        @return: the splunk web server address.
        @rtype: string
        """
        return "{scheme}://{host}:{web_port}".format(
            scheme=self.web_scheme(), host=self.web_host(), web_port=self.web_port()
        )

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

    def create_connector(self, **kwargs):
        """
        @param kwargs:
        @return:
        """
        kwargs["username"] = self.username
        kwargs["password"] = self.password

        conn = SDKConnector(self, **kwargs)

        connector_id = self._get_connector_id(user=conn.username)

        if connector_id in list(self._connectors.keys()):
            LOGGER.warning(f"Connector {connector_id} is being replaced")
            del self._connectors[connector_id]
        self._connectors[connector_id] = conn

        return self._connectors[connector_id]

    def create_logged_in_connector(self, set_as_default=False, **kwargs):
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

        @return: The newly created, logged in, connector
        """
        conn = self.create_connector(**kwargs)
        if set_as_default:
            self._default_connector = conn
        conn.login()
        return conn

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

    def _get_connector_id(self, user):
        """
        Returns the connector id

        @param user: splunk username used by connector
        @type user: string
        """
        return f"{user}"

    @property
    def default_connector(self):
        """
        Returns the default connector for this Splunk instance.

        This method caches the value so it isn't created on every call.
        """
        if self._default_connector is None:
            self._default_connector = self.create_logged_in_connector(
                set_as_default=True
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

    def connector(self):
        if self.username is None:
            return self.default_connector

        connector_id = self._get_connector_id(self.username)
        if connector_id not in list(self._connectors.keys()):
            raise InvalidConnector(f"Connector {connector_id} does not exist")
        connector = self._connectors[connector_id]
        self._attempt_login(connector)
        return connector

    def jobs(self):
        """
        Returns a Jobs manager that uses the specified connector. Defaults to
        default connector if none specified.

        This property creates a new Jobs manager each call so you may do as
        you please with it.

        @rtype: L{Jobs}
        """
        from pytest_splunk_addon.helmut.manager.jobs.sdk import SDKJobsWrapper

        return SDKJobsWrapper(self.connector())

    def get_event_count(self, search_string="*"):
        """
        Displatches a search job and returns an event count without waiting for indexing to finish
        @param search_string: The search string
        """
        LOGGER.info("Getting event count")
        jobs = SDKJobsWrapper(self.default_connector)
        job = jobs.create("search %s" % search_string)
        job.wait()
        event_count = job.get_event_count()
        LOGGER.debug(f"Event count: {event_count}")
        return event_count

    def get_final_event_count(
        self, search_string="*", secondsToStable=60, retry_interval=30
    ):
        """
        Waits until indexing is done and then gives the final event count that the search reported.
        @param search_string: The search string
        @param secondsToStable: The time to wait with stable index before we decide indexing is done
        @param retry_interval: wait time b/w two successive search jobs
        """
        resultPrev = -1
        resultSameSince = sys.maxsize
        lastPolledAt = int(time.time())
        while True:
            time.sleep(retry_interval)
            result = self.get_event_count(search_string=search_string)
            now = int(
                time.time()
            )  # time()'s precision will suffice here, and in fact seconds is all we want
            if result == resultPrev:
                if (now - resultSameSince) > secondsToStable:  ### we have stable state
                    LOGGER.info(
                        "Achieved stable state for search %s with totalEventCount=%s"
                        % (search_string, result)
                    )
                    return result  # returns the final event count...
                if (
                    resultSameSince == sys.maxsize
                ):  ### our first time in what could become stable state
                    LOGGER.debug(
                        "Possibly entering stable state for search %s at totalEventCount=%s"
                        % (search_string, result)
                    )
                    resultSameSince = lastPolledAt
                    LOGGER.debug("Using resultSameSince=%d " % (resultSameSince))
                else:  ### our 2nd/3rd/... time in what could become stable state
                    LOGGER.debug(
                        "Confirming putative stable at totalEventCount=%s for search_string %s "
                        % (result, search_string)
                    )
            else:  ### we do NOT have stable state
                LOGGER.debug(
                    "Flux at totalEventCount=%s for search_string %s; delta +%s"
                    % (result, search_string, (result - resultPrev))
                )
                resultPrev = result
                resultSameSince = sys.maxsize
            lastPolledAt = now

    def ensure_event_count(
        self, search_string, expect_count, retry=3, retry_interval=10
    ):
        """
        @param search_string:
        @param retry:
        @param retry_interval:
        @return:

        ensure event count met in given tries, return true if met, else false
        """
        event_count = 0
        while retry > 0:
            event_count = self.get_final_event_count(search_string, secondsToStable=120)
            if event_count == expect_count:
                (
                    "event count met. event_count={event_count}".format(
                        event_count=str(event_count)
                    )
                )
                return True
            else:
                LOGGER.debug(
                    "wait event count to met. event_count={event_count}".format(
                        event_count=str(event_count)
                    )
                )
            time.sleep(retry_interval)
            retry = retry - 1
        LOGGER.debug(
            "Timeout wait event count to met. event_count={event_count}".format(
                event_count=str(event_count)
            )
        )
        return False


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
        super().__init__(message)


class InvalidConnector(KeyError):
    """
    Raised when accessing an invalid connector
    """

    pass
