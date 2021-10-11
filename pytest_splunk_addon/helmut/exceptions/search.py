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
class SearchFailure(RuntimeError):
    """
    This exception is raised when a search fails and returns the error through sdk get_message function.
    """

    def __init__(self, search_message):
        self.search_message = search_message
        super(SearchFailure, self).__init__(self._error_message)

    @property
    def _error_message(self):
        message = "Search failed with Error: {0}"
        return message.format(self.search_message)
