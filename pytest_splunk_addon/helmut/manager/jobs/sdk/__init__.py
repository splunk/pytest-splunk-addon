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
