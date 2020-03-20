"""
@author: Nicklas Ansman-Giertz
@contact: U{ngiertz@splunk.com<mailto:ngiertz@splunk.com>}
@since: 2011-11-23
"""
import splunklib.results as results

from pytest_splunk_addon.helmut.manager.jobs.job import Job
from pytest_splunk_addon.helmut.manager.jobs.results import Results


class SDKJobWrapper(Job):
    def __init__(self, sdk_connector, sdk_job):
        """
        The constructor of the SDKJobWrapper.

        @param sdk_connector: The SDKConnector object used to connect to Splunk.
        @type param: SDKConnector
        @param sdk_job: The Job object from the Python SDK.
        @type param: splunklib.client.Job
        """
        self._raw_sdk_job = sdk_job

        super(SDKJobWrapper, self).__init__(sdk_connector)

    @property
    def raw_sdk_job(self):
        return self._raw_sdk_job

    @property
    def sid(self):
        return self.raw_sdk_job.sid

    def __str__(self):
        return "SDK Job with SID {sid}".format(sid=self.sid)

    # Endpoint specific

    def get_request(self):
        return self.raw_sdk_job.refresh().content.request

    def get_event_count(self):
        return int(self.raw_sdk_job.refresh().content.eventCount)

    def get_scan_count(self):
        return int(self.raw_sdk_job.refresh().content.scanCount)

    def get_event_available_count(self):
        return int(self.raw_sdk_job.refresh().content.eventAvailableCount)

    def get_result_count(self):
        return int(self.raw_sdk_job.refresh().content.resultCount)

    def get_cursor_time(self):
        return self.raw_sdk_job.refresh().content.cursorTime

    def is_done(self):
        return self.raw_sdk_job.is_done()

    def is_failed(self):
        return self.raw_sdk_job.refresh().content.isFailed == "1"

    def is_finalized(self):
        return self.raw_sdk_job.refresh().content.isFinalized == "1"

    def is_saved(self):
        return self.raw_sdk_job.refresh().content.isSaved == "1"

    def get_keywords(self):
        return self.raw_sdk_job.refresh().content.keywords

    def is_paused(self):
        return self.raw_sdk_job.refresh().content.isPaused == "1"

    def result_is_streaming(self):
        return self.raw_sdk_job.refresh().content.resultIsStreaming == "1"

    def get_messages(self):
        return self.raw_sdk_job.refresh().content.messages

    def get_ttl(self):
        return int(self.raw_sdk_job.refresh().content.ttl)

    def set_ttl(self, value):
        self.logger.info("Setting job %s TTL to: %s" % (self.sid, value))
        self.raw_sdk_job.set_ttl(value)
        return self

    def get_error(self):
        return self.raw_sdk_job.refresh().content.error

    def get_earliest_time(self):
        return self.raw_sdk_job.refresh().content.earliestTime

    def get_latest_time(self):
        return self.raw_sdk_job.refresh().content.latestTime

    def get_run_duration(self):
        return float(self.raw_sdk_job.refresh().content.runDuration)

    def get_event_search(self):
        return self.raw_sdk_job.refresh().content.eventSearch

    def event_is_streaming(self):
        return self.raw_sdk_job.refresh().content.eventIsStreaming == "1"

    def get_event_sorting(self):
        val = self.raw_sdk_job.refresh().content.eventSorting
        return None if val == "none" else val

    def get_report_search(self):
        return self.raw_sdk_job.refresh().content.reportSearch

    def get_remote_search(self):
        return self.raw_sdk_job.refresh().content.remoteSearch

    def event_is_truncated(self):
        return self.raw_sdk_job.refresh().content.eventIsTruncated == "1"

    def get_label(self):
        return self.raw_sdk_job.refresh().content.label

    def get_dispatch_state(self):
        return self.raw_sdk_job.refresh().content.dispatchState

    def is_saved_search(self):
        return self.raw_sdk_job.refresh().content.isSavedSearch == "1"

    def is_zombie(self):
        return self.raw_sdk_job.refresh().content.isZombie == "1"

    def get_search_providers(self):
        return self.raw_sdk_job.refresh().content.searchProviders

    def get_status_buckets(self):
        return int(self.raw_sdk_job.refresh().content.statusBuckets)

    def get_done_progress(self):
        return self.raw_sdk_job.refresh().content.doneProgress

    # The methods below are forwarding calls to the job

    def cancel(self):
        self.logger.info("Cancelling job, SID: %s" % self.sid)
        self.raw_sdk_job.cancel()
        return self

    def disable_preview(self):
        self.logger.info("Disabling preview for job, SID: %s" % self.sid)
        self.raw_sdk_job.disable_preview()
        return self

    def get_events(self, **kwargs):
        response = self.raw_sdk_job.events(**kwargs)
        return _build_results_from_sdk_response(response)

    def get_events_dict(self, **kwargs):
        response = self.raw_sdk_job.events(**kwargs)
        return _build_events_from_sdk_response(response)

    def get_results_dict(self, **kwargs):
        response = self.raw_sdk_job.results(**kwargs)
        return _build_results_dict_from_sdk_response(response)

    def enable_preview(self):
        self.logger.info("Enabling preview for job, SID: %s" % self.sid)
        self.raw_sdk_job.enable_preview()
        return self

    def finalize(self):
        self.logger.info("Finalizing job, SID: %s" % self.sid)
        self.raw_sdk_job.finalize()
        return self

    def pause(self):
        self.logger.info("Pausing job, SID: %s" % self.sid)
        self.raw_sdk_job.pause()
        return self

    def unpause(self):
        self.logger.info("Unpausing job, SID: %s" % self.sid)
        self.raw_sdk_job.unpause()
        return self

    def get_preview(self, **kwargs):
        response = self.raw_sdk_job.preview(**kwargs)
        return _build_results_from_sdk_response(response)

    def get_results(self, **kwargs):
        response = self.raw_sdk_job.results(**kwargs)
        return _build_results_from_sdk_response(response)

    def get_search_log(self, **kwargs):
        return self.raw_sdk_job.searchlog(**kwargs)

    def set_priority(self, value):
        self.logger.info("Setting priority of job %s to: %s" % (self.sid, value))
        self.raw_sdk_job.set_priority(value)
        return self

    # unfinished see JIRA AUTO-62
    def get_summary(self, **kwargs):
        self.logger.warn("get_summary() is not fully implemented.")
        return self.raw_sdk_job.refresh().summary(**kwargs)

    # unfinished see JIRA AUTO-62
    def get_timeline(self, **kwargs):
        self.logger.warn("get_timeline() is not fully implemented.")
        return self.raw_sdk_job.refresh().timeline(**kwargs)

    def touch(self):
        self.logger.info("Touching job, SID: %s" % self.sid)
        self.raw_sdk_job.touch()
        return self


def _build_results_from_sdk_response(response):
    """
    Get results from the SDK and return them.
    """
    reader = results.ResultsReader(response)
    events = []
    for result in reader:
        events.append(_build_event_from_results_reader(result))
    return Results(events)


def _build_results_dict_from_sdk_response(response):
    """
    Get results from the SDK and return them.
    """
    reader = results.ResultsReader(response)
    resultset = []
    for result in reader:
        resultset.append(result)
    return resultset


def _build_events_from_sdk_response(response):
    """
    Get results from the SDK and return them.
    """
    reader = results.ResultsReader(response)
    events = []
    for result in reader:
        events.append(_build_event_from_results_reader(result))
    return events


def _build_event_from_results_reader(reader):
    """
    Creates an event as a dict from an event in the SDK.
    """
    event = {}
    for field in list(reader.keys()):
        event[field] = reader[field]
    return event
