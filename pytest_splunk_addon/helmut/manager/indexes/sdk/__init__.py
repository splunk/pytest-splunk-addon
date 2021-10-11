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
@author: Nicklas Ansman-Giertz
@contact: U{ngiertz@splunk.com<mailto:ngiertz@splunk.com>}
@since: 2011-11-23
"""
from splunklib.client import HTTPError

from pytest_splunk_addon.helmut.manager.indexes import IndexNotFound
from pytest_splunk_addon.helmut.manager.indexes import Indexes
from pytest_splunk_addon.helmut.manager.indexes.sdk.index import SDKIndexWrapper


class SDKIndexesWrapper(Indexes):
    """
    The Indexes subclass that wraps the Splunk Python SDK's Indexes object.
    It basically contains a collection of L{SDKIndexWrapper}s.
    """

    @property
    def _service(self):
        return self.connector.service

    def create_index(self, index_name):
        try:
            self.logger.info("Creating index '%s'" % index_name)
            self.connector.service.indexes.create(index_name)
        except HTTPError as err:
            # Index already exists
            if not err.status == 409:
                raise
            self.logger.warn(
                "Index '%s' already exists. HTTPError: %s" % (index_name, err)
            )
        return self[index_name]

    def __getitem__(self, index_name):
        for index in self:
            if index.name == index_name:
                return index
        raise IndexNotFound(index_name)

    def __contains__(self, index_name):
        for index in self:
            if index.name == index_name:
                return True
        return False

    def items(self):
        indexes = self._service.indexes
        return [SDKIndexWrapper(self.connector, index) for index in indexes]
