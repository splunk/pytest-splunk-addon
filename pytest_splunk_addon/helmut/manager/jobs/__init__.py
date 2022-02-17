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
from pytest_splunk_addon.helmut.misc.manager_utils import (
    create_wrapper_from_connector_mapping,
)


class Jobs:
    """
    Jobs is the manager that handles searches.
    It does not handle pausing, resuming, etc of individual searches, it just
    spawns and lists searches.
    """

    def __init__(self, connector):
        self._connector = connector

    def __new__(cls, connector):
        mappings = _CONNECTOR_TO_WRAPPER_MAPPINGS
        return create_wrapper_from_connector_mapping(cls, connector, mappings)

    def create(self, query, **kwargs):
        pass

    def items(self):
        """
        Return a collection of all the contained objects. It is up to the
        subclass to decide whether this collection is a list, map or of any
        other kind.

        @return: A collection of all the items contained.
        """
        pass

    def __contains__(self, item):
        """
        Return boolean whether item is contained in Collection.

        @param item: The item which is checked if contained.
        """
        pass

    def __call__(self):
        return list(self.items())

    def __len__(self):
        return len(list(self.items()))

    def __iter__(self):
        for item in list(self.items()):
            yield item

    def __getitem__(self, sid):
        pass


class JobNotFound(RuntimeError):
    def __init__(self, sid):
        self.sid = sid
        super(JobNotFound, self).__init__(self._error_message)

    @property
    def _error_message(self):
        return "Could not find a job with SID {sid}".format(sid=self.sid)


# We need this at the bottom to avoid cyclic imports

from pytest_splunk_addon.helmut.connector.sdk import SDKConnector
from pytest_splunk_addon.helmut.manager.jobs.sdk import SDKJobsWrapper

_CONNECTOR_TO_WRAPPER_MAPPINGS = {
    SDKConnector: SDKJobsWrapper,
}
