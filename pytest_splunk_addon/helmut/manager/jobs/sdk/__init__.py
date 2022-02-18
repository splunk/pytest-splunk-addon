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

from pytest_splunk_addon.helmut.exceptions.job import JobNotFound
from pytest_splunk_addon.helmut.manager.jobs.sdk.job import SDKJobWrapper

LOGGER = logging.getLogger("helmut")


class SDKJobsWrapper:
    def __init__(self, connector):
        self._connector = connector

    @property
    def _service(self):
        return self._connector.service

    def create(self, query, **kwargs):
        LOGGER.info("Creating job with query: %s" % query)
        job = self._service.jobs.create(query, **kwargs)
        return SDKJobWrapper(self._connector, job)

    def __call__(self):
        return list(self.items())

    def __len__(self):
        return len(list(self.items()))

    def __iter__(self):
        for item in list(self.items()):
            yield item

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

    def items(self):
        jobs = self._service.jobs
        return [SDKJobWrapper(self._connector, job) for job in jobs]
