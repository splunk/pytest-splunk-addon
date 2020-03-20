from __future__ import absolute_import

import sys
import time
import traceback
from builtins import str

from splunklib.binding import HTTPError

from pytest_splunk_addon.helmut.connector.base import Connector
from pytest_splunk_addon.helmut.manager.jobs import Jobs
from .base import Splunk


class CloudSplunk(Splunk):
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
        super(CloudSplunk, self).__init__(name)
        self.set_credentials_to_use(username=username, password=password)

        server_web_scheme = server_web_host = server_web_port = None
        if not (web_scheme and web_host):
            try:
                sdkconn = self.create_logged_in_connector(contype=Connector.SDK)
                server_settings = sdkconn.service.settings
                server_web_scheme = (
                    "http" if server_settings["enableSplunkWebSSL"] == "0" else "https"
                )
                server_web_host = server_settings["host"]
                server_web_port = server_settings["httpport"]
                self._pass4SymmKey = server_settings["pass4SymmKey"]
            except HTTPError as he:
                self.logger.warning(
                    "No sufficient permissions to qury server settings."
                )
        self._web_scheme = web_scheme or server_web_scheme or "http"
        self._web_host = web_host or server_web_host or self._splunkd_host
        self._web_port = web_port or server_web_port or ""
        self.logger.debug("Set web base to: {}".format(self.web_base()))

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
            sdkconn = self.create_logged_in_connector(contype=Connector.SDK)
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

    def create_connector(
        self, contype=None, username=None, password=None, *args, **kwargs
    ):
        """
        @param contype:
        @param username: Don't use this parameter. This is only for backward compatible. CloudSplunk
                        only uses self.username as connector's username.
        @param password: Don't use this parameter. This is only for backward compatible.
        @param args:
        @param kwargs:
        @return:
        """
        if (
            username
            and username != self.username
            and password
            and password != self.password
        ):
            raise CloudSplunkConnectorException()
        return super(CloudSplunk, self).create_connector(
            contype=contype, username=username, password=password, *args, **kwargs
        )

    def connector(self, contype=None, username=None):
        """

        @param contype:
        @param username: Don't use this parameter. This is only for backward compatible. CloudSplunk
                        only uses self.username as connector's username.
        @return:
        """
        if username and username != self.username:
            raise CloudSplunkConnectorException()
        return super(CloudSplunk, self).connector(contype=contype, username=username)

    def get_host_os(self):
        raise NotImplementedError("Host os should not matter for CloudSplunk.")

    def is_running(self):
        restconn = self.create_connector(contype=Connector.REST)
        try:
            response, _ = restconn.make_request("GET", "/services/server/info")
            return response["status"] == restconn.SUCCESS["GET"]
        except Exception:
            self.logger.debug("Not able to make GET request." + traceback.format_exc())
            return False

    def restart(self):
        raise CloudRestartException()

    def get_event_count(self, search_string="*"):
        """
        Displatches a search job and returns an event count without waiting for indexing to finish
        @param search_string: The search string
        """
        self.logger.info("Getting event count")
        event_count = 0
        jobs = Jobs(self.default_connector)
        job = jobs.create("search %s" % search_string)
        job.wait()
        event_count = job.get_event_count()
        self.logger.debug("Event count: {ec}".format(ec=event_count))
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
        counts = []
        while True:
            time.sleep(retry_interval)
            result = self.get_event_count(search_string=search_string)
            now = int(
                time.time()
            )  # time()'s precision will suffice here, and in fact seconds is all we want
            if result == resultPrev:
                if (now - resultSameSince) > secondsToStable:  ### we have stable state
                    self.logger.info(
                        "Achieved stable state for search %s with totalEventCount=%s"
                        % (search_string, result)
                    )
                    return result  # returns the final event count...
                if (
                    resultSameSince == sys.maxsize
                ):  ### our first time in what could become stable state
                    self.logger.debug(
                        "Possibly entering stable state for search %s at totalEventCount=%s"
                        % (search_string, result)
                    )
                    resultSameSince = lastPolledAt
                    self.logger.debug("Using resultSameSince=%d " % (resultSameSince))
                else:  ### our 2nd/3rd/... time in what could become stable state
                    self.logger.debug(
                        "Confirming putative stable at totalEventCount=%s for search_string %s "
                        % (result, search_string)
                    )
            else:  ### we do NOT have stable state
                self.logger.debug(
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
                self.logger.debug(
                    "wait event count to met. event_count={event_count}".format(
                        event_count=str(event_count)
                    )
                )
            time.sleep(retry_interval)
            retry = retry - 1
        self.logger.debug(
            "Timeout wait event count to met. event_count={event_count}".format(
                event_count=str(event_count)
            )
        )
        return False


class CloudSplunkConnectorException(Exception):
    message = (
        "Don't pass username/password to connector. Helmut allows only one user per CloudSplunk instance."
        "Please create another CloudSplunk instance if you need to use another user."
    )


class CloudRestartException(Exception):
    message = "Restart on cloud is prohibited unless you are using cloud ops role."
