"""
@author: Lei Zhang
@contact: U{leiz@splunk.com<mailto:leiz@splunk.com>}
@since: 2018-05-01
"""
import json
from builtins import object
from builtins import range

from pytest_splunk_addon.helmut.manager.confs import Confs
from pytest_splunk_addon.helmut.manager.confs import (
    PATH_PERFIX,
    PATH_CONF,
    PATH_PROPERTIES,
)
from pytest_splunk_addon.helmut.manager.confs.rest.conf import RESTConfWrapper
from pytest_splunk_addon.helmut.util.string_unicode_convert import (
    normalize_to_str,
    normalize_to_unicode,
)


class RESTConfsWrapper(Confs):
    """
        The Confs subclass that is associated with the RESTConnector.
    """

    @property
    def _service(self):
        return self.connector

    def __getitem__(self, conf_name):
        for conf in self:
            if conf.name == conf_name:
                return conf
        raise ConfNotFound(conf_name)

    def create(self, conf_name):
        conf_name = normalize_to_unicode(conf_name)
        if conf_name in self:
            self.logger.info("conf file '%s' already existed" % conf_name)
            return

        self.logger.info("Creating conf file %s" % conf_name)
        # create(conf_name)
        return RESTConfWrapper(self.connector, self._create(conf_name))

    def items(self):
        conf_names = self.list()
        #        for c in conf_names:
        #            print c.name
        return [RESTConfWrapper(self.connector, conf_name) for conf_name in conf_names]

    def list(self):
        # return conf object
        conf_list = []
        url = PATH_PERFIX + PATH_PROPERTIES
        req_args = {"output_mode": "json"}
        response, content = self.connector.make_request("GET", url, req_args)
        assert response["status"] == "200"
        parsed_content = json.loads(content)
        for i in range(len(parsed_content["entry"])):
            conf_list.append(parsed_content["entry"][i]["name"])
        return [Configurations(self.connector, conf_name) for conf_name in conf_list]

    def _create(self, conf_name):
        conf_name = normalize_to_str(conf_name)
        url = PATH_PERFIX + PATH_PROPERTIES
        user_args = {"__conf": conf_name}
        response, content = self.connector.make_request(
            "POST", url, user_args, {"output_mode": "json"}
        )
        assert response["status"] == "201"
        if conf_name in self:
            return Configurations(self.connector, conf_name)


class ConfNotFound(RuntimeError):
    """
    Raised when a conf file that does not exist is read from.

    @ivar conf: The name of the conf that did not exist.
    """

    def __init__(self, conf):
        """
        Creates a new exception.

        @param conf: The name of the conf file that was missing.
        """
        self.conf = conf
        super(ConfNotFound, self).__init__(self._error_message)

    @property
    def _error_message(self):
        """
        The error message for this exception.

        @rtype: str
        """
        msg = "The conf file {conf}.conf doesn't exist"
        return msg.format(conf=self.conf)


class Configurations(object):
    """
    wraps a Config object using Splunk REST connector
    """

    def __init__(self, connector, conf_name):
        self.connector = connector
        self._name = conf_name
        self._path = PATH_CONF % conf_name

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path
