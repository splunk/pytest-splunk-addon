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
class WaitTimedOut(RuntimeError):
    """
    This exception is raised when a designated wait period times out.
    """

    def __init__(self, seconds_waited):
        self.seconds_waited = seconds_waited
        super(WaitTimedOut, self).__init__(self._error_message)

    @property
    def _error_message(self):
        message = "Search was not done after {0} seconds"
        return message.format(self.seconds_waited)


class DownloadTimedOut(RuntimeError):
    """
    This exception is raise when release doesnt return the package
    """

    pass


class ExecuteTimeOut(RuntimeError):
    """
    This exception is raise when execute function time out
    """

    pass


class Md5CheckFailed(RuntimeError):
    """
    This exception is raise when MD5 check failed
    """

    pass
