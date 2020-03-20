"""
@author: Nicklas Ansman-Giertz
@contact: U{ngiertz@splunk.com<mailto:ngiertz@splunk.com>}
@since: 2011-11-23
"""
import time
from abc import abstractmethod, abstractproperty
from builtins import str

from pytest_splunk_addon.helmut.exceptions.search import SearchFailure
from pytest_splunk_addon.helmut.exceptions.wait import WaitTimedOut
from pytest_splunk_addon.helmut.manager.object import ItemFromManager


class Job(ItemFromManager):
    """
    Job handles the individual searches that spawn jobs. This manager has the
    ability to stop, pause, finalize, etc jobs. You can also retrieve
    different data about the job such as event count.
    """

    _SECONDS_BETWEEN_JOB_IS_DONE_CHECKS = 1

    @abstractmethod
    def get_results(self, **kwargs):
        pass

    @abstractmethod
    def is_done(self):
        pass

    @abstractmethod
    def is_failed(self):
        pass

    @abstractmethod
    def get_messages(self):
        pass

    @abstractproperty
    def sid(self):
        pass

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
        self.logger.debug("Waiting for job to finish.")
        if timeout == 0:
            timeout = None

        start_time = time.time()
        while not self.is_done():
            try:
                if self.is_failed():
                    self.logger.warn(
                        "job %s failed. error message: %s"
                        % (self.sid, self.get_messages())
                    )
                    break
            except AttributeError as e:
                self.logger.debug(str(e))
            _check_if_wait_has_timed_out(start_time, timeout)
            time.sleep(self._SECONDS_BETWEEN_JOB_IS_DONE_CHECKS)

        self.logger.debug("Job %s wait is done." % self.sid)
        return self

    def check_message(self):
        if self.get_messages():
            message = self.get_messages()
            for key in message:
                if key == "error":
                    raise SearchFailure(message[key])


def _check_if_wait_has_timed_out(start_time, timeout):
    if timeout is None:
        return
    if _wait_timed_out(start_time, timeout):
        raise WaitTimedOut(timeout)


def _wait_timed_out(start_time, timeout):
    return time.time() > start_time + timeout
