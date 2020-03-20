"""
@author: Annie Ju
@contact: U{xju@splunk.com<mailto:xju@splunk.com>}
@since: 2018-06-14
"""

import json
from builtins import object
from builtins import range

from pytest_splunk_addon.helmut.manager.jobs import (
    Jobs,
    JobNotFound,
    PATH_PERFIX,
    CONTROL,
    EVENTS,
    RESULTS,
    RESULTS_PREVIEW,
    SEARCHLOG,
    SUMMARY,
    TIMELINE,
)
from pytest_splunk_addon.helmut.manager.jobs.rest.job import RESTJobWrapper
from pytest_splunk_addon.helmut.util.string_unicode_convert import normalize_to_str


class RESTJobsWrapper(Jobs):
    def create(self, query, **kwargs):
        self.logger.info("Creating job with query: %s" % query)
        job = self._create(query, **kwargs)
        return RESTJobWrapper(self.connector, job)

    def _create(self, query, **kwargs):
        query = normalize_to_str(query)
        url = PATH_PERFIX
        user_args = {"search": query}
        kwargs = dict(
            [normalize_to_str(k), normalize_to_str(v)] for k, v in kwargs.items()
        )
        args = user_args.copy()
        args.update(kwargs)
        response, content = self.connector.make_request(
            "POST", url, args, {"output_mode": "json"}
        )
        assert response["status"] == "201"
        parsed_content = json.loads(content)
        return RestJob(self.connector, parsed_content["sid"])

    def __contains__(self, sid):
        for job in self:
            if job.sid == sid:
                return True
        return False

    def __getitem__(self, sid):
        for job in self:
            if job.sid == sid:
                return job
        raise JobNotFound(sid)

    # Required from Collection

    def items(self):
        jobs = self._service.jobs
        return [RESTJobWrapper(self.connector, job) for job in jobs]

    def _list_job(self):
        job_list = []
        url = PATH_PERFIX
        req_args = {"output_mode": "json"}
        response, content = self.connector.make_request("GET", url, req_args)
        assert response["status"] == "200"
        parsed_content = json.loads(content)
        for i in range(len(parsed_content["entry"])):
            job_list.append(parsed_content["entry"][i]["name"])
        return [RestJob(self.connector, index_name) for index_name in job_list]


class RestJob(object):
    """
    wraps a Job object using Splunk REST connector
    """

    def __init__(self, connector, sid):
        self.connector = connector
        self._sid = sid

    @property
    def sid(self):
        return self._sid

    def refresh(self):
        sid = self._sid
        url = PATH_PERFIX + sid
        req_args = {"output_mode": "json"}
        response, content = self.connector.make_request("GET", url, urlparam=req_args)
        assert response["status"] == "200"
        parsed_content = json.loads(content)
        return parsed_content["entry"][0]

    def update_search(self, **kwargs):
        sid = self._sid
        kwargs = dict(
            [normalize_to_str(k), normalize_to_str(v)] for k, v in kwargs.items()
        )
        url = PATH_PERFIX + sid
        req_args = {"output_mode": "json"}
        response, content = self.connector.make_request(
            "POST", url, body=kwargs, urlparam=req_args
        )
        assert response["status"] == "200"

    def delete_search(self, **kwargs):
        sid = self._sid
        kwargs = dict(
            [normalize_to_str(k), normalize_to_str(v)] for k, v in kwargs.items()
        )
        url = PATH_PERFIX + sid
        req_args = {"output_mode": "json"}
        response, content = self.connector.make_request(
            "DELETE", url, body=kwargs, urlparam=req_args
        )
        assert response["status"] == "200"

    def control_search(self, **kwargs):
        sid = self._sid
        kwargs = dict(
            [normalize_to_str(k), normalize_to_str(v)] for k, v in kwargs.items()
        )
        url = PATH_PERFIX + sid + CONTROL
        req_args = {"output_mode": "json"}
        response, content = self.connector.make_request(
            "POST", url, body=kwargs, urlparam=req_args
        )
        assert response["status"] == "200"
        return json.loads(content)

    def get_search_events(self, **kwargs):
        sid = self._sid
        url = PATH_PERFIX + sid + EVENTS
        req_args = {"output_mode": "json", "segmentation": "none"}
        kwargs = dict(
            [normalize_to_str(k), normalize_to_str(v)] for k, v in kwargs.items()
        )
        args = req_args.copy()
        args.update(kwargs)
        response, content = self.connector.make_request("GET", url, urlparam=args)
        assert response["status"] == "200"
        return content

    def get_search_results(self, **kwargs):
        sid = self._sid
        url = PATH_PERFIX + sid + RESULTS
        req_args = {"output_mode": "json", "segmentation": "none"}
        kwargs = dict(
            [normalize_to_str(k), normalize_to_str(v)] for k, v in kwargs.items()
        )
        args = req_args.copy()
        args.update(kwargs)
        # Refer to INFRA-17464, get search result should not be recorded in ..log,
        # otherwise, the ..log might be too large to open.
        response, content = self.connector.make_request(
            "GET", url, urlparam=args, log_response=False
        )
        assert response["status"] == "200"
        return content

    def get_search_results_preview(self, **kwargs):
        sid = self._sid
        url = PATH_PERFIX + sid + RESULTS_PREVIEW
        req_args = {"output_mode": "json", "segmentation": "none"}
        kwargs = dict(
            [normalize_to_str(k), normalize_to_str(v)] for k, v in kwargs.items()
        )
        args = req_args.copy()
        args.update(kwargs)
        # Refer to INFRA-17464, get search result preview should not be recorded in ..log,
        # otherwise, the ..log might be too large to open.
        response, content = self.connector.make_request(
            "GET", url, urlparam=args, log_response=False
        )
        assert response["status"] == "200"
        return content

    def get_search_log(self, **kwargs):
        sid = self._sid
        url = PATH_PERFIX + sid + SEARCHLOG
        req_args = {"output_mode": "json", "segmentation": "none"}
        kwargs = dict(
            [normalize_to_str(k), normalize_to_str(v)] for k, v in kwargs.items()
        )
        args = req_args.copy()
        args.update(kwargs)
        response, content = self.connector.make_request("GET", url, urlparam=args)
        assert response["status"] == "200"
        return content

    def get_search_summary(self, **kwargs):
        sid = self._sid
        url = PATH_PERFIX + sid + SUMMARY
        req_args = {"output_mode": "json", "segmentation": "none"}
        kwargs = dict(
            [normalize_to_str(k), normalize_to_str(v)] for k, v in kwargs.items()
        )
        args = req_args.copy()
        args.update(kwargs)
        response, content = self.connector.make_request("GET", url, urlparam=args)
        return content

    def get_search_timeline(self, **kwargs):
        sid = self._sid
        url = PATH_PERFIX + sid + TIMELINE
        req_args = {"output_mode": "json", "segmentation": "none"}
        kwargs = dict(
            [normalize_to_str(k), normalize_to_str(v)] for k, v in kwargs.items()
        )
        args = req_args.copy()
        args.update(kwargs)
        response, content = self.connector.make_request("GET", url, urlparam=args)
        return content
