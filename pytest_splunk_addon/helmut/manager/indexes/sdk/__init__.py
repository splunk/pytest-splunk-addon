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
