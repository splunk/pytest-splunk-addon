"""
@author: Sagar Bhatnagar
"""

from future import standard_library

standard_library.install_aliases()
from builtins import str
from .base import Connector
import urllib.request, urllib.parse, urllib.error
import httplib2
from pytest_splunk_addon.helmut.exceptions import AuthenticationError
import json
import xml.etree.ElementTree as et
from xml.dom.minidom import parseString
import time


class RESTConnector(Connector):
    """
    This represents workaround to access REST thru HTTP client library httplib2

    Associated with each object is a C{http} object from the httplib which in
    turn contains connection info, namespace and auth.

    When a connector is logged in a sessionkey is generated and will be kept
    until the point that you logout or the server is restarted.

    When Splunk is restarted the connector I{tries} to login again

    @ivar _service: The underlying service, aka the http request object
    @cvar HEADERS: The default headers to pass with http request. this will
    get appended with the 'Authorization' key when sessionkey is used

    """

    HEADERS = {"content-type": "text/xml; charset=utf-8"}
    METHODS = ["GET", "POST", "PUT", "DELETE"]
    SUCCESS = {"GET": "200", "POST": "201", "DELETE": "200", "PUT": "200"}

    DEFAULT_OWNER = "admin"
    DEFAULT_APP = (
        "search"  # defaulting it search app for the case when app is not passed.
    )

    def __init__(self, splunk, username=None, password=None, app=None, owner=None):
        """
         Creates a new REST connector.

         The connector will logged in when created with default values

         @param splunk: The Splunk instance
         @type splunk: L{..splunk.Splunk}
         @param username: The username to use. If None (default)
                          L{Connector.DEFAULT_USERNAME} is used.
         @type username: str
         @param password: The password to use. If None (default)
                          L{Connector.DEFAULT_PASSWORD} is used.
         @type password: str
         @param app: The app to use.This will construct namespace <ownerr>:<app>
         @type app: str
         @param app: The owner to use.This will construct namespace <ownerr>:<app>
         @type app: str

        """
        super(RESTConnector, self).__init__(
            splunk, username=username, password=password, owner=owner, app=app,
        )
        self.uri_base = splunk.uri_base()
        self._timeout = 60
        self._debug_level = 0
        self._disable_ssl_certificate = True
        self._follow_redirects = False
        httplib2.debuglevel = self._debug_level
        self.sessionkey = None
        self._service = httplib2.Http(
            timeout=self._timeout,
            disable_ssl_certificate_validation=self._disable_ssl_certificate,
        )
        self._service.follow_redirects = self._follow_redirects
        self._service.add_credentials(self._username, self._password)

        splunk.register_start_listener(self)

    @property
    def namespace(self):
        """
        The namespace for this RESTconnector.

        Will be in the format /<owner>/<app>

        @rtype: str
        """
        return "/" + str(self._owner) + "/" + str(self._app)

    def make_request(
        self,
        method,
        uri,
        body=None,
        urlparam=None,
        use_sessionkey=False,
        log_response=True,
    ):
        """
        Make a HTTP request to an endpoint

        @type  method: string
        @param method: HTTP valid methods: PUT, GET, POST, DELETE
        @type  uri: string
        @param uri: URI of the REST endpoint
        @type  body: string or dictionary or a sequence of two-element tuples
        @param body: the request body
        @type  urlparam: string/ dictionary or a sequence of two-element tuples
        @param urlparam: the URL parameters
        @type  use_sessionkey: bool
        @param use_sessionkey: toggle for using sessionkey or not
        @type  log_response: bool
        @param log_response: log the response to ..log or not

        >>> conn.make_request('POST', '/services/receivers/simple',
        urlparam={'host': 'foo'}, body="my event")

        """
        if body is None:
            body = ""
        if type(body) != str and type(body) != str:
            body = urllib.parse.urlencode(body)
        if urlparam is None:
            urlparam = ""
        if type(urlparam) != str:
            urlparam = urllib.parse.urlencode(urlparam)
        if urlparam != "":
            url = "%s%s?%s" % (self.uri_base, uri, urlparam)
        else:
            url = "%s%s" % (self.uri_base, uri)

        if use_sessionkey:
            self._service.clear_credentials()
            self.update_headers("Authorization", "Splunk %s" % self.sessionkey)
        else:
            if not self._service.credentials.credentials:
                self._service.add_credentials(self._username, self._password)
            if "Authorization" in self.HEADERS:
                self.HEADERS.pop("Authorization")
        response, content = self._service.request(
            url, method, body=body, headers=self.HEADERS
        )

        self.logger.info(
            "Request  => {r}".format(
                r={
                    "method": method,
                    "url": url,
                    "body": body,
                    "auth": "{u}:{p}".format(u=self._username, p=self._password),
                    "header": self.HEADERS,
                }
            )
        )
        if log_response:
            self.logger.info("Response => {r}".format(r=response))
            self.logger.debug("Content  => {c}".format(c=content))

        return response, content

    def make_requestNS(
        self,
        method,
        uri,
        body=None,
        urlparam=None,
        use_sessionkey=False,
        log_response=True,
    ):

        """
        Wrapper on top of make_request. For uri, don't use any of /services
        or /serviceNS,just pass the endpoint,it will read the namespace from
        connector itself

        @type  method: string
        @param method: HTTP valid methods: PUT, GET, POST, DELETE
        @type  uri: string
        @param uri: URI of the REST endpoint
        @type  body: string or dictionary or a sequence of two-element tuples
        @param body: the request body
        @type  urlparam: string/ dictionary or a sequence of two-element tuples
        @param urlparam: the URL parameters
        @type  use_sessionkey: bool
        @param use_sessionkey: toggle for using sessionkey or not
        @type  log_response: bool
        @param log_response: log the response to ..log or not

        >>> conn.make_requestNS('GET', 'data/outputs/tcp/default')

        """
        uri = "/servicesNS" + self.namespace + uri
        response, content = self.make_request(
            method,
            uri,
            body,
            urlparam=urlparam,
            use_sessionkey=use_sessionkey,
            log_response=log_response,
        )
        return response, content

    def parse_content_json(self, content):
        """
        Parses the content object (in json format) to python dict

        @type content: json
        @param content: content object from http request in json format
        """

        return json.loads(str(content))

    @property
    def _service_arguments(self):
        """
        The arguments to pass to the Service (httplib in this case).

        If makes sure that they have default values if nothing is specified.

        @rtype: dict
        @return: default values for the httplib service

        """
        return {
            "username": self._username,
            "password": self._password,
            "namespace": self.namespace,
            "uri_base": self.splunk.uri_base(),
        }

    def _recreate_service(self):
        """
        Clones the current service with the same values.

        It then tries to log the service in if the old one was logged in.
        Called when Splunk starts
        """
        _was_logged_in = self._was_logged_in()
        service = self._clone_existing_service()
        self._service = service
        self.uri_base = self._service_arguments["uri_base"]
        if _was_logged_in:
            try:
                self.login()
            except AuthenticationError as autherr:
                self.logger.warn(
                    "RESTConnector for username:{username} password:{password}"
                    " login failed when recreating service. error msg:{error}".format(
                        username=self.username,
                        password=self.password,
                        error=autherr.message,
                    )
                )

    def login(self):
        """
         Logs the connector in.

         Just hits the auth endpoint and retreives and sets the sessionkey.

        """
        body = urllib.parse.urlencode(
            {"username": self._username, "password": self._password}
        )
        url = "%s%s" % (self.uri_base, "/services/auth/login")
        response, content = self._service.request(url, "POST", body=body)
        self._attempt_login_time = time.time()
        if response.status != 200:
            msg = "Login failed... response status: %s content: %s" % (
                response.status,
                content,
            )
            self.logger.warn(msg)
            raise AuthenticationError(msg)

        root = et.fromstring(str(content))
        self.sessionkey = root[0].text
        if not self._service.credentials.credentials:
            self._service.add_credentials(self._username, self._password)

    def _clone_existing_service(self):
        """
         clones the existing service

         @return: The newly created service (httplib) http object
         @rtype: http object
        """
        http = httplib2.Http(
            timeout=self._timeout,
            disable_ssl_certificate_validation=self._disable_ssl_certificate,
        )
        http.follow_redirects = False
        http.add_credentials(
            self._service_arguments["username"], self._service_arguments["password"]
        )
        return http

    def logout(self):
        """
        Logs the connector out

        This just unsets the sessionkey.

        """
        if "Authorization" in self.HEADERS:
            self.HEADERS.pop("Authorization")
        self.sessionkey = None
        self._service.clear_credentials()

    def is_logged_in(self):
        """
        Checks if the connector is logged in.

        This checks if the sessionkey is set and is not expired.
        @return: True if the connector is logged in
        @rtype: bool

        """
        if self.sessionkey is None:
            return False
        elif self._is_session_expired():
            return False
        else:
            return True

    def _was_logged_in(self):
        """
        Checks if the connector was logged in.

        This checks if the sessionkey is set.
        :return:
        """
        return self.sessionkey is not None

    def _is_session_expired(self):
        """
        Checks if the session key is an expired one.

        Hits an endpoint with that key and check response status is 401
        """
        url = "%s%s" % (self.uri_base, "/services/data/outputs/tcp/default")
        self._service.clear_credentials()
        self.update_headers("Authorization", "Splunk %s" % self.sessionkey)
        response, content = self._service.request(url, "GET", headers=self.HEADERS)
        self._service.add_credentials(self._username, self._password)
        if response["status"] == "401":
            self.logger.debug(
                "Session is expired for RESTconnector %s:%s"
                % (self.username, self.password)
            )
            return True
        else:
            self.logger.debug(
                "Session is NOT expired for RESTconnector %s:%s"
                % (self.username, self.password)
            )
            return False

    def update_headers(self, key=None, value=None):
        """
        Appends a key,value pair to the HEADERS

        @type key: str
        @param key: key to append to  HEADERS
        @type value: str
        @param value: value for that key to append to  HEADERS

        """
        if key in self.HEADERS:
            self.HEADERS.pop(key)
        self.HEADERS.update({key: value})

    def debug_level(self, value):
        """
        Overrides default value for debug_level  for httplib service

        @type value: int
        @param value: debugging level

        """

        self._debug_level = value

    def timeout(self, value):
        """
        Overrides default value for timout for http request

        @type value: int
        @param value: timeout for the http request in seconds

        """

        self._timeout = value

    def disable_ssl_certificate(self, value):
        """
        Overrides disable sssl certificate condition

        @type value: bool
        @param value: enable/disable ssl certificate for auth

        """

        self._disable_ssl_certificate = value

    def follow_redirects(self, value):
        """
        Overrides default value of the follow_redircets

        @type value: bool
        @param value: follow redirects

        """

        self._follow_redirects = value

    def __del__(self):
        """
        Called when the object is being deallocated.

        It unregisters itself with the Splunk start listeners.

        """
        self.splunk.unregister_start_listener(self)

    def __call__(self):
        """
        Called when the splunk instance class notifies REST connector listener

        Need  it as local splunk instance notify method invokes l() and then
        service will be recreated and initialized with default values
        """
        self._recreate_service()

    def parse_content_xml(self, content, tag):
        """
        Parses the content object (in xml format)

        @type content: xml
        @param content: content object from http request in xml format

        """
        dom = parseString(content)
        xmlTag = dom.getElementsByTagName(tag)[0].toxml()
        return xmlTag
