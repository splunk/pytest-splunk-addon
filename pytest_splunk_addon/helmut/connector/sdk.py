"""
This module handles connections through the public python SDK.

@author: Nicklas Ansman-Giertz
@contact: U{ngiertz@splunk.com<mailto:ngiertz@splunk.com>}
@since: 2011-11-09
"""
import time

from splunklib.binding import _NoAuthenticationToken, AuthenticationError
from splunklib.client import Service, Endpoint

from .base import Connector


class SDKConnector(Connector):
    """
    This class represents one connection through the public python SDK.

    One connection means one session.
    If you have multiple, identical, SDKConnectors it represents having
    multiple login from the same user.

    Associated with each object is a C{Service} object from the SDK which in
    turn contains connection info, namespace and auth.

    When a connector is logged in an auth token is generated and will be kept
    until the point that you logout or the server is restarted.

    The connector reads ports, host and scheme from the given Splunk instance.
    When Splunk is restarted the info is read again to reflect any changes
    that were made.

    When Splunk is restarted the connector I{tries} to login again if the
    connector was logged in before. This might not always work (if you disabled
    auth for instance) though.

    The Python SDK, as of version 0.8.0, uses separate parameters to evaluate
    the namespace. Therefor the primary parameters to be used are 'owner', 'app'
    and 'sharing' instead of namespace. See splunklib.binding for more info.

    @ivar _service: The underlying service
    @cvar DEFAULT_SHARING: The default sharing option, as defined by the
                        Python SDK in splunklib.binding, that will be used
                        if it isn't specified by the user.
    @cvar DEFAULT_OWNER: The default owner that will be used if it isn't
                        specified by the user.
    @cvar DEFAULT_APP: The default app that will be used if it isn't
                        specified by the user.
    """

    DEFAULT_SHARING = "system"
    DEFAULT_HANDLER = None

    # TODO: TEMPORARY FOR EST-1859
    PATH_SERVER_SETTINGS = "server/settings/settings/"

    def __init__(
        self,
        splunk,
        username=None,
        password=None,
        namespace=None,
        sharing=DEFAULT_SHARING,
        owner=None,
        app=None,
    ):
        """
        Creates a new connector.

        The connector will not be logged in when created so you have to manually
        login.

        @param splunk: The Splunk instance
        @type splunk: L{..splunk.Splunk}
        @param username: The username to use. If None (default)
                         L{Connector.DEFAULT_USERNAME} is used.
        @type username: str
        @param password: The password to use. If None (default)
                         L{Connector.DEFAULT_PASSWORD} is used.
        @type password: str
        @param namespace: Deprecated. user owner and app instead.
        @type namespace: str
        @param sharing: used by python sdk service
        @type sharing: str
        @param owner: used by python sdk service
        @type owner: str
        @param app: used by python sdk service
        @type app: str
        """

        super(SDKConnector, self).__init__(
            splunk, username=username, password=password, owner=owner, app=app
        )
        if namespace is not None and namespace != self.namespace:
            msg = (
                "namespace is derecated. please use owner and app. "
                "Your namespace setting : %s, owner&app setting:%s"
                % (namespace, self.namespace)
            )
            self.logger.error(msg)
            raise Exception(msg)
        self.sharing = (
            sharing  # accepting None value, so SDK takes owner and app blindly.
        )

        self._service = Service(handler=self.DEFAULT_HANDLER, **self._service_arguments)
        splunk.register_start_listener(self._recreate_service)

        # TODO: TEMPORARY FOR EST-1859
        self._server_settings_endpoint = Endpoint(
            self._service, self.PATH_SERVER_SETTINGS
        )

    @property
    def _service_arguments(self):
        """
        The arguments to pass to the Service.

        If makes sure that they have default values if nothing is specified.

        @rtype: dict
        """
        return {
            "username": self.username,
            "password": self.password,
            # No longer used by SDK's splunklib.binding since 0.8.0 (beta)
            # 'namespace': self.namespace,
            "owner": self.owner,
            "app": self.app,
            "sharing": self.sharing,
            "scheme": self.splunk.splunkd_scheme(),
            "host": self.splunk.splunkd_host(),
            "port": self.splunk.splunkd_port(),
        }

    def __del__(self):
        """
        Called when the object is being deallocated.
        It unregisters itself with the Splunk start listeners.
        """
        self.splunk.unregister_start_listener(self._recreate_service)

    def _recreate_service(self):
        """
        Clones the current service with the same values.
        It then tries to log the service in if the old one was logged in.

        Called when Splunk starts.
        """
        self.logger.debug("Recreating and cloning the current Service.")
        _was_logged_in = self._was_logged_in()
        service = self._clone_existing_service()
        self._service = service
        if _was_logged_in:
            try:
                self.login()
            except AuthenticationError as autherr:
                self.logger.warn(
                    "SDKConnector for username:{username} password:{password}"
                    " login failed when recreating service. error msg:{error}".format(
                        username=self.username,
                        password=self.password,
                        error=autherr.message,
                    )
                )

        # TODO: TEMPORARY FOR EST-1859
        self._server_settings_endpoint = Endpoint(
            self._service, self.PATH_SERVER_SETTINGS
        )

    def _clone_existing_service(self):
        """
        Clones the existing service with the exception that it re-reads the
        connection info from the Splunk instance.

        @return: The newly created Service
        @rtype: Service
        """
        return Service(handler=self.DEFAULT_HANDLER, **self._service_arguments)

    @property
    def service(self):
        """
        The Service that is connected with this connector.

        The Service is the object that comes from the public SDK.

        @rtype: Service
        """
        return self._service

    # TODO: TEMPORARY FOR EST-1859
    @property
    def server_settings_endpoint(self):
        return self._server_settings_endpoint

    def is_logged_in(self):
        """
        Checks if the connector is logged in.

        Hits an endpoint and check if AuthenticationError is raised.

        @return: True if the connector is logged in
        @rtype: bool
        """
        try:
            self._service.get("authentication/current-context")
            # FAST-8222
        except AuthenticationError as err:
            self.logger.debug(
                "SDKconnector %s:%s is NOT logged in" % (self.username, self.password)
            )
            return False
        else:
            self.logger.debug(
                "SDKconnector %s:%s is logged in" % (self.username, self.password)
            )
            return True

    def _was_logged_in(self):
        """
        Checks if the connector was logged in.

        This checks if the service.token is set.
        :return:
        """
        return self._service.token is not _NoAuthenticationToken

    def login(self):
        """
        Logs the connector in.

        Just calls the login method on the service object.

        @return: self
        @rtype: SDKConnector
        """
        self.logger.debug("Logging in the connector.")
        self._attempt_login_time = time.time()
        self.service.login()
        return self

    def logout(self):
        """
        Logs the connector out by calling the logout method on the service.

        This in turn just unsets the auth token.

        @return: self
        @rtype: SDKConnector
        """
        self.logger.debug("Logging out the connector.")
        self.service.logout()
        return self
