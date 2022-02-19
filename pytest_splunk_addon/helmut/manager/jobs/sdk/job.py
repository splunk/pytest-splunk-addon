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
import time

import splunklib.results as results

from pytest_splunk_addon.helmut.manager.jobs.results import Results
from pytest_splunk_addon.helmut.exceptions.search import SearchFailure
from pytest_splunk_addon.helmut.exceptions.wait import WaitTimedOut

LOGGER = logging.getLogger("helmut")


class SDKJobWrapper:
    _SECONDS_BETWEEN_JOB_IS_DONE_CHECKS = 1

    def __init__(self, sdk_connector, sdk_job):
        """
        The constructor of the SDKJobWrapper.

        @param sdk_connector: The SDKConnector object used to connect to Splunk.
        @type param: SDKConnector
        @param sdk_job: The Job object from the Python SDK.
        @type param: splunklib.client.Job
        """
        self._raw_sdk_job = sdk_job
        self._connector = sdk_connector

    @property
    def raw_sdk_job(self):
        return self._raw_sdk_job

    @property
    def sid(self):
        return self.raw_sdk_job.sid

    def __str__(self):
        return f"SDK Job with SID {self.sid}"

    def get_event_count(self):
        return int(self.raw_sdk_job.refresh().content.eventCount)

    def get_result_count(self):
        return int(self.raw_sdk_job.refresh().content.resultCount)

    def is_done(self):
        return self.raw_sdk_job.is_done()

    def is_failed(self):
        return self.raw_sdk_job.refresh().content.isFailed == "1"

    def get_messages(self):
        return self.raw_sdk_job.refresh().content.messages

    def cancel(self):
        LOGGER.info("Cancelling job, SID: %s" % self.sid)
        self.raw_sdk_job.cancel()
        return self

    def get_events(self, **kwargs):
        response = self.raw_sdk_job.events(**kwargs)
        return _build_results_from_sdk_response(response)

    def get_results(self, **kwargs):
        response = self.raw_sdk_job.results(**kwargs)
        return _build_results_from_sdk_response(response)

    def wait(self, timeout=5400):
        """
        Waits for this search to finish.

        @param timeout: The maximum time to wait in seconds. None or 0
                        means no limit, None is default.
        @type timeout: int
        @return: self
        @rtype: L{SDKJobWrapper}
        @raise WaitTimedOut: If the search isn't done after
                                  C{timeout} seconds.
        """
        LOGGER.debug("Waiting for job to finish.")
        if timeout == 0:
            timeout = None

        start_time = time.time()
        while not self.is_done():
            try:
                if self.is_failed():
                    LOGGER.warn(
                        "job %s failed. error message: %s"
                        % (self.sid, self.get_messages())
                    )
                    break
            except AttributeError as e:
                LOGGER.debug(str(e))
            _check_if_wait_has_timed_out(start_time, timeout)
            time.sleep(self._SECONDS_BETWEEN_JOB_IS_DONE_CHECKS)

        LOGGER.debug("Job %s wait is done." % self.sid)
        return self

    def check_message(self):
        if self.get_messages():
            message = self.get_messages()
            for key in message:
                if key == "error":
                    raise SearchFailure(message[key])


def _build_results_from_sdk_response(response):
    """
    Get results from the SDK and return them.
    """
    reader = results.ResultsReader(response)
    events = []
    for result in reader:
        events.append(_build_event_from_results_reader(result))
    return Results(events)


def _build_event_from_results_reader(reader):
    """
    Creates an event as a dict from an event in the SDK.
    """
    event = {}
    for field in list(reader.keys()):
        event[field] = reader[field]
    return event


def _check_if_wait_has_timed_out(start_time, timeout):
    if timeout is None:
        return
    if _wait_timed_out(start_time, timeout):
        raise WaitTimedOut(timeout)


def _wait_timed_out(start_time, timeout):
    return time.time() > start_time + timeout
