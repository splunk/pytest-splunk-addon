"""
@author: Annie Ju
@contact: U{xju@splunk.com<mailto:xju@splunk.com>}
@since: 2018-06-14
"""
from future import standard_library

standard_library.install_aliases()
from pytest_splunk_addon.helmut.manager.jobs.results import Results
from pytest_splunk_addon.helmut.manager.jobs.job import Job
import json


class RESTJobWrapper(Job):
    def __init__(self, rest_connector, rest_job):
        """
        The constructor of the RESTJobWrapper.

        @param rest_connector: The RESTConnector object used to connect to Splunk.
        @type param: RESTConnector
        @param rest_job: The Job object from the Python REST.
        @type param: splunklib.client.Job
        """
        super(RESTJobWrapper, self).__init__(rest_connector)
        self._raw_rest_job = rest_job

    @property
    def raw_rest_job(self):
        return self._raw_rest_job

    @property
    def sid(self):
        return self.raw_rest_job.sid

    def __str__(self):
        return "REST Job with SID {sid}".format(sid=self.sid)

    # Endpoint specific
    def get_request(self):
        result = self.raw_rest_job.refresh()
        return result["content"]["request"]

    def get_event_count(self):
        result = self.raw_rest_job.refresh()
        return (
            int(result["content"]["eventCount"])
            if "eventCount" in result["content"]
            else 0
        )

    def get_scan_count(self):
        result = self.raw_rest_job.refresh()
        return (
            int(result["content"]["scanCount"])
            if "scanCount" in result["content"]
            else 0
        )

    def get_event_available_count(self):
        result = self.raw_rest_job.refresh()
        return (
            int(result["content"]["eventAvailableCount"])
            if "eventAvailableCount" in result["content"]
            else 0
        )

    def get_result_count(self):
        result = self.raw_rest_job.refresh()
        return (
            int(result["content"]["resultCount"])
            if "resultCount" in result["content"]
            else 0
        )

    def get_cursor_time(self):
        result = self.raw_rest_job.refresh()
        return result["content"]["cursorTime"]

    def is_preview_enabled(self):
        result = self.raw_rest_job.refresh()
        return bool(result["content"]["isPreviewEnabled"])

    def is_done(self):
        result = self.raw_rest_job.refresh()
        return bool(result["content"]["isDone"])

    def is_failed(self):
        result = self.raw_rest_job.refresh()
        return bool(result["content"]["isFailed"])

    def is_finalized(self):
        result = self.raw_rest_job.refresh()
        return bool(result["content"]["isFinalized"])

    def is_saved(self):
        result = self.raw_rest_job.refresh()
        return bool(result["content"]["isSaved"])

    def get_keywords(self):
        result = self.raw_rest_job.refresh()
        return result["content"]["keywords"]

    def is_paused(self):
        result = self.raw_rest_job.refresh()
        return bool(result["content"]["isPaused"])

    def result_is_streaming(self):
        result = self.raw_rest_job.refresh()
        return bool(result["content"]["resultIsStreaming"])

    def get_messages(self):
        result = self.raw_rest_job.refresh()
        return result["content"]["messages"]

    def get_ttl(self):
        result = self.raw_rest_job.refresh()
        return result["content"]["ttl"]

    def set_ttl(self, value):
        self.logger.info("Setting job %s TTL to: %s" % (self.sid, value))
        response = self.raw_rest_job.control_search(action="setttl", ttl=value)
        assert (
            "The ttl of the search job was changed to {value}".format(value=value)
            in response["messages"][0]["text"]
        )
        return self

    def get_error(self):
        result = self.raw_rest_job.refresh()
        return result["content"]["error"] if "error" in result["content"] else None

    def get_earliest_time(self):
        result = self.raw_rest_job.refresh()
        return result["content"]["earliestTime"]

    def get_latest_time(self):
        result = self.raw_rest_job.refresh()
        return (
            result["content"]["latestTime"]
            if "latestTime" in result["content"]
            else None
        )

    def get_run_duration(self):
        result = self.raw_rest_job.refresh()
        return float(result["content"]["runDuration"])

    def get_event_search(self):
        result = self.raw_rest_job.refresh()
        return result["content"]["eventSearch"]

    def event_is_streaming(self):
        result = self.raw_rest_job.refresh()
        return bool(result["content"]["eventIsStreaming"])

    def get_event_sorting(self):
        result = self.raw_rest_job.refresh()
        val = result["content"]["eventSorting"]
        return None if val == "none" else val

    def get_report_search(self):
        result = self.raw_rest_job.refresh()
        return result["content"]["reportSearch"]

    def get_remote_search(self):
        result = self.raw_rest_job.refresh()
        return result["content"]["remoteSearch"]

    def event_is_truncated(self):
        result = self.raw_rest_job.refresh()
        return bool(result["content"]["eventIsTruncated"])

    def get_label(self):
        result = self.raw_rest_job.refresh()
        return result["content"]["label"]

    def get_dispatch_state(self):
        result = self.raw_rest_job.refresh()
        return result["content"]["dispatchState"]

    def is_saved_search(self):
        result = self.raw_rest_job.refresh()
        return bool(result["content"]["isSavedSearch"])

    def is_zombie(self):
        result = self.raw_rest_job.refresh()
        return bool(result["content"]["isZombie"])

    def get_search_providers(self):
        result = self.raw_rest_job.refresh()
        return result["content"]["searchProviders"]

    def get_status_buckets(self):
        result = self.raw_rest_job.refresh()
        return int(result["content"]["statusBuckets"])

    def get_done_progress(self):
        result = self.raw_rest_job.refresh()
        return int(result["content"]["doneProgress"])

    # The methods below are forwarding calls to the job
    def cancel(self):
        self.logger.info("Cancelling job, SID: %s" % self.sid)
        response = self.raw_rest_job.control_search(action="cancel")
        assert "cancelled" in response["messages"][0]["text"]
        return self

    def disable_preview(self):
        self.logger.info("Disabling preview for job, SID: %s" % self.sid)
        response = self.raw_rest_job.control_search(action="disablepreview")
        assert response["messages"][0]["text"] == "Search job results preview disabled."
        return self

    def get_events(self, **kwargs):
        response = self.raw_rest_job.get_search_events(**kwargs)
        return _build_results_from_rest_response(response)

    def get_events_dict(self, **kwargs):
        response = self.raw_rest_job.get_search_events(**kwargs)
        return _build_events_from_rest_response(response)

    def get_results_dict(self, **kwargs):
        response = self.raw_rest_job.get_search_results(**kwargs)
        return _build_results_dict_from_rest_response(response)

    def enable_preview(self):
        self.logger.info("Enabling preview for job, SID: %s" % self.sid)
        response = self.raw_rest_job.control_search(action="enablepreview")
        assert response["messages"][0]["text"] == "Search job results preview enabled."
        return self

    def finalize(self):
        self.logger.info("Finalizing job, SID: %s" % self.sid)
        response = self.raw_rest_job.control_search(action="finalize")
        assert "finalized" in response["messages"][0]["text"]
        return self

    def pause(self):
        self.logger.info("Pausing job, SID: %s" % self.sid)
        response = self.raw_rest_job.control_search(action="pause")
        assert "paused" in response["messages"][0]["text"]
        return self

    def unpause(self):
        self.logger.info("Unpausing job, SID: %s" % self.sid)
        response = self.raw_rest_job.control_search(action="unpause")
        assert "unpaused" in response["messages"][0]["text"]
        return self

    def get_preview(self, **kwargs):
        response = self.raw_rest_job.get_search_results_preview(**kwargs)
        return _build_results_from_rest_response(response)

    def get_results(self, **kwargs):
        response = self.raw_rest_job.get_search_results(**kwargs)
        return _build_results_from_rest_response(response)

    def get_search_log(self, **kwargs):
        return self.raw_rest_job.get_search_log(**kwargs)

    def set_priority(self, value):
        self.logger.info("Setting priority of job %s to: %s" % (self.sid, value))
        response = self.raw_rest_job.control_search(
            action="setpriority", priority=value
        )
        assert (
            "The search job's priority was changed" in response["messages"][0]["text"]
        )
        return self

    def get_summary(self, **kwargs):
        response = self.raw_rest_job.get_search_summary(**kwargs)
        return _build_results_from_rest_response(response) if response != "" else ""

    def get_timeline(self, **kwargs):
        response = self.raw_rest_job.get_search_timeline(**kwargs)
        return response

    def touch(self):
        self.logger.info("Touching job, SID: %s" % self.sid)
        response = self.raw_rest_job.control_search(action="touch")
        assert "touched" in response["messages"][0]["text"]
        return self


def _build_results_from_rest_response(response):
    """
    Get results from the REST and return them.
    """
    events = json.loads(response)["results"]
    return Results(events)


def _build_results_dict_from_rest_response(response):
    """
    Get results from the REST and return them.
    """
    events = json.loads(response)["results"]
    return events


def _build_events_from_rest_response(response):
    """
    Get results from the REST and return them.
    """
    events = json.loads(response)["results"]
    return events
