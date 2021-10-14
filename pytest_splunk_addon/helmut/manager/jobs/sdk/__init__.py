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
"""
This module is a specialized version of the search_manager module for the SDK

@author: Nicklas Ansman-Giertz
@contact: U{ngiertz@splunk.com<mailto:ngiertz@splunk.com>}
@since: 2011-11-23
"""

from pytest_splunk_addon.helmut.manager.jobs import Jobs, JobNotFound
from pytest_splunk_addon.helmut.manager.jobs.sdk.job import SDKJobWrapper


class SDKJobsWrapper(Jobs):
    @property
    def _service(self):
        return self.connector.service

    def create(self, query, **kwargs):
        self.logger.info("Creating job with query: %s" % query)
        job = self._service.jobs.create(query, **kwargs)
        return SDKJobWrapper(self.connector, job)

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
        return [SDKJobWrapper(self.connector, job) for job in jobs]
