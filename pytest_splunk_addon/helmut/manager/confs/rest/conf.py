"""
@author: Lei Zhang
@contact: U{leiz@splunk.com<mailto:leiz@splunk.com>}
@since: 2018-05-01
"""
from future import standard_library

standard_library.install_aliases()
from builtins import range
from builtins import object
from splunklib.client import HTTPError

from pytest_splunk_addon.helmut.manager.confs.conf import Conf
from pytest_splunk_addon.helmut.manager.confs.rest.stanza import RESTStanzaWrapper
from pytest_splunk_addon.helmut.exceptions.confs import StanzaNotFound
from pytest_splunk_addon.helmut.manager.confs import PATH_PERFIX, COUNT_OFFSET
from pytest_splunk_addon.helmut.util.string_unicode_convert import (
    normalize_to_str,
    normalize_to_unicode,
)
import json
import urllib.request, urllib.parse, urllib.error


class RESTConfWrapper(Conf):
    """
       The L{Conf} object corresponding to a Conf object in the Splunk REST API.
       It holds a set of L{RESTStanza}s.
    """

    def __init__(self, rest_connector, rest_conf):
        super(RESTConfWrapper, self).__init__(rest_connector, rest_conf.name)
        self._raw_rest_conf = rest_conf

    @property
    def raw_rest_conf(self):
        return self._raw_rest_conf

    def __getitem__(self, stanza_name):
        for stanza in self:
            if stanza.name == stanza_name:
                return stanza
        raise StanzaNotFound(self.name, stanza_name)

    def stanzas_list(self,):
        stanza_list = []
        url = PATH_PERFIX + self._raw_rest_conf.path + COUNT_OFFSET
        req_args = {"output_mode": "json"}
        response, content = self.connector.make_request("GET", url, req_args)
        assert response["status"] == "200"
        parsed_content = json.loads(content)
        for i in range(len(parsed_content["entry"])):
            stanza_list.append(parsed_content["entry"][i]["name"])
        return [
            RestStanza(self.connector, self._raw_rest_conf, stanza_name)
            for stanza_name in stanza_list
        ]

    def _create_stanza(self, stanza_name, **values):
        if stanza_name in self:
            return RestStanza(self.connector, self._raw_rest_conf, stanza_name)
        values = dict(
            [normalize_to_str(k), normalize_to_str(v)] for k, v in values.items()
        )
        stanza_name = normalize_to_str(stanza_name)
        url = PATH_PERFIX + self._raw_rest_conf.path
        user_args = {"name": stanza_name}
        user_args.update(values)
        response, content = self.connector.make_request(
            "POST", url, user_args, {"output_mode": "json"}
        )
        assert response["status"] == "201"
        if normalize_to_unicode(stanza_name) in self:
            return RestStanza(self.connector, self._raw_rest_conf, stanza_name)

    def _delete_stanza(self, stanza_name):
        stanza_name = normalize_to_str(stanza_name)
        url = (
            PATH_PERFIX
            + self._raw_rest_conf.path
            + "/{stanza_name}".format(stanza_name=stanza_name)
        )
        self.connector.make_request("DELETE", url)

    def items(self):
        stanzas = self.stanzas_list()
        return [RESTStanzaWrapper(self, stanza) for stanza in stanzas]

    def create_stanza(self, stanza_name, values=None):
        values = values or {}
        values = dict(
            [normalize_to_unicode(k), normalize_to_unicode(v)]
            for k, v in values.items()
        )
        stanza_name = normalize_to_unicode(stanza_name)
        try:
            self.logger.info(
                "Creating stanza '%s' in %s.conf with values:"
                " %s." % (stanza_name, self.name, values)
            )
            return RESTStanzaWrapper(self, self._create_stanza(stanza_name, **values))
        except HTTPError as h:
            self.logger.warn(
                "Stanza '%s' already existed in %s.conf. "
                "HTTPError message: %s" % (stanza_name, self.name, h)
            )
            return self[stanza_name]
        except Exception:
            raise

    def delete_stanza(self, stanza_name):
        stanza_name = normalize_to_unicode(stanza_name)
        try:
            self.logger.info(
                "Deleting stanza '%s' in %s.conf" % (stanza_name, self.name)
            )
            self._delete_stanza(stanza_name)
        except HTTPError as h:
            self.logger.warn("Error during deletion: %s" % h)
        except Exception:
            raise


class RestStanza(object):
    """
    wraps a Stanza object using Splunk REST connector
    """

    def __init__(self, connector, rest_conf, rest_stanza_name):
        self.connector = connector
        self.rest_conf = rest_conf
        self._name = rest_stanza_name

    @property
    def name(self):
        return self._name

    @property
    def content(self):
        return self._content()

    def _content(self):
        name = urllib.parse.quote_plus(self._name)
        url = (
            PATH_PERFIX + self.rest_conf.path + "{stanza_name}".format(stanza_name=name)
        )
        req_args = {"output_mode": "json"}
        response, content = self.connector.make_request("GET", url, req_args)
        assert response["status"] == "200"
        parsed_content = json.loads(content)
        return parsed_content["entry"][0]["content"]

    def update(self, **values):
        values = dict(
            [normalize_to_str(k), normalize_to_str(v)] for k, v in values.items()
        )
        name = urllib.parse.quote_plus(self._name)
        url = (
            PATH_PERFIX + self.rest_conf.path + "{stanza_name}".format(stanza_name=name)
        )
        user_args = values
        response, content = self.connector.make_request(
            "POST", url, user_args, {"output_mode": "json"}
        )
        assert response["status"] == "200"

    def refresh(self,):
        name = urllib.parse.quote_plus(self._name)
        url = (
            PATH_PERFIX + self.rest_conf.path + "{stanza_name}".format(stanza_name=name)
        )
        req_args = {"output_mode": "json"}
        response, content = self.connector.make_request("GET", url, req_args)
        assert response["status"] == "200"
