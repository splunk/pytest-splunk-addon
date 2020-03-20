"""
@author: Lei Zhang
@contact: U{leiz@splunk.com<mailto:leiz@splunk.com>}
@since: 2018-06-11
"""
from future import standard_library

standard_library.install_aliases()
from builtins import range
from future.utils import raise_
from builtins import object
from splunklib.client import HTTPError

from pytest_splunk_addon.helmut.manager.indexes import Indexes
from pytest_splunk_addon.helmut.manager.indexes.rest.index import RESTIndexWrapper
from pytest_splunk_addon.helmut.manager.indexes import (
    IndexNotFound,
    PATH_PERFIX,
    COUNT_OFFSET,
    DISABLE,
    SYSTEM_MESSAGE,
    RESTART,
    ENABLE,
    ROLL_HOT_BUCKETS,
    OperationError,
)
from pytest_splunk_addon.helmut.util.string_unicode_convert import (
    normalize_to_str,
    normalize_to_unicode,
)
import json
import urllib.request, urllib.parse, urllib.error
from datetime import datetime, timedelta
import time


class RESTIndexesWrapper(Indexes):
    """
    The Indexes subclass that wraps the Splunk REST Indexes object.
    It basically contains a collection of L{RestIndexWrapper}s.
    """

    def create_index(self, index_name):
        index_name = normalize_to_unicode(index_name)
        try:
            self.logger.info("Creating index '%s'" % index_name)
            self._create_index(index_name)
        except HTTPError as err:
            # Index already exists
            if not err.status == 409:
                raise
            self.logger.warn(
                "Index '%s' already exists. HTTPError: %s" % (index_name, err)
            )
        return self[index_name]

    def _create_index(self, index_name):
        index_name = normalize_to_str(index_name)
        url = PATH_PERFIX
        user_args = {"name": index_name}
        response, content = self.connector.make_request(
            "POST", url, user_args, {"output_mode": "json"}
        )
        assert response["status"] == "201"
        if normalize_to_unicode(index_name) in self:
            return RestIndex(self.connector, index_name)

    def _list_index(self):
        index_list = []
        url = PATH_PERFIX + COUNT_OFFSET
        req_args = {"output_mode": "json"}
        response, content = self.connector.make_request("GET", url, req_args)
        assert response["status"] == "200"
        parsed_content = json.loads(content)
        for i in range(len(parsed_content["entry"])):
            index_list.append(parsed_content["entry"][i]["name"])
        return [RestIndex(self.connector, index_name) for index_name in index_list]

    def __getitem__(self, index_name):
        for index in self:
            if index.name == index_name:
                return index
        raise IndexNotFound(index_name)

    def __contains__(self, index_name):
        for index in self:
            if index.name == index_name:
                return True
        return False

    def items(self):
        indexes = self._list_index()
        return [RESTIndexWrapper(self.connector, index) for index in indexes]


class RestIndex(object):
    """
    wraps a Index object using Splunk REST connector
    """

    def __init__(self, connector, index_name):
        self.connector = connector
        self._name = index_name
        self.result = None

    @property
    def name(self):
        return self._name

    def encode_name(self):
        return urllib.parse.quote_plus(self._name)

    def refresh(self):
        name = self.encode_name()
        url = PATH_PERFIX + name
        req_args = {"output_mode": "json"}
        response, content = self.connector.make_request("GET", url, req_args)
        assert response["status"] == "200"
        parsed_content = json.loads(content)
        return parsed_content["entry"][0]

    def clean(self, timeout):
        try:
            result = self.refresh()
            tds = result["content"]["maxTotalDataSizeMB"]
            ftp = result["content"]["frozenTimePeriodInSecs"]
            self.update(maxTotalDataSizeMB=1, frozenTimePeriodInSecs=1)
            self.roll_hot_buckets()
            diff = timedelta(seconds=timeout)
            start = datetime.now()
            Done = False
            while not Done and datetime.now() < start + diff:
                time.sleep(1)
                res = self.refresh()
                if int(res["content"]["totalEventCount"]) == 0:
                    Done = True
            if not Done:
                raise_(
                    OperationError,
                    "Cleaning index %s took longer than %s seconds; timing out."
                    % (self._name, timeout),
                )
        finally:
            self.update(maxTotalDataSizeMB=tds, frozenTimePeriodInSecs=ftp)

    def disable(self):
        name = self.encode_name()
        url = PATH_PERFIX + name + DISABLE
        req_args = {"output_mode": "json"}
        response, content = self.connector.make_request("POST", url, req_args)
        assert response["status"] == "200"
        if self.restart_required():
            self.restart(120)

    def enable(self):
        name = self.encode_name()
        url = PATH_PERFIX + name + ENABLE
        req_args = {"output_mode": "json"}
        response, content = self.connector.make_request("POST", url, req_args)
        assert response["status"] == "200"

    def update(self, **kwargs):
        name = self.encode_name()
        kwargs = dict(
            [normalize_to_str(k), normalize_to_str(v)] for k, v in kwargs.items()
        )
        url = PATH_PERFIX + name
        req_args = {"output_mode": "json"}
        response, content = self.connector.make_request("POST", url, kwargs, req_args)
        assert response["status"] == "200"

    def delete(self, **kwargs):
        name = self.encode_name()
        kwargs = dict(
            [normalize_to_str(k), normalize_to_str(v)] for k, v in kwargs.items()
        )
        url = PATH_PERFIX + name
        response, content = self.connector.make_request("DELETE", url)
        assert response["status"] == "200"

    def roll_hot_buckets(self,):
        name = self.encode_name()
        url = PATH_PERFIX + name + ROLL_HOT_BUCKETS
        req_args = {"output_mode": "json"}
        response, content = self.connector.make_request("POST", url, req_args)
        assert response["status"] == "200"

    def restart_required(self):
        url = SYSTEM_MESSAGE
        req_args = {"output_mode": "json"}
        response, content = self.connector.make_request("GET", url, req_args)
        assert response["status"] == "200"
        parsed_content = json.loads(content)
        if len(parsed_content["entry"]) == 0:
            return False
        else:
            for entry in parsed_content["entry"]:
                if "restart_required" in entry["title"]:
                    return True
        return False

    def restart(self, timeout=None):
        msg = {"value": "Restart requested by Splunk Helumt RestIndex Oject"}
        url = SYSTEM_MESSAGE
        user_args = {"name": "restart_required", "value": msg}
        response, content = self.connector.make_request(
            "POST", url, user_args, {"output_mode": "json"}
        )
        assert response["status"] == "201"
        response, content = self.connector.make_request(
            "POST", RESTART, {"output_mode": "json"}
        )
        assert response["status"] == "200"
        result = json.loads(content)
        if timeout is None:
            return result
        start = datetime.now()
        diff = timedelta(seconds=timeout)
        while datetime.now() - start < diff:
            try:
                time.sleep(1)
                if self.login(self.connector) and not self.restart_required():
                    return result
            except Exception as e:
                time.sleep(1)
        raise Exception("Operation time out.")

    def login(self, connector):
        if (
            hasattr(connector, "is_logged_in")
            and connector._attempt_login_time > 0
            and not connector.is_logged_in()
        ):
            connector.login()
            return connector.is_logged_in()
        else:
            return False
