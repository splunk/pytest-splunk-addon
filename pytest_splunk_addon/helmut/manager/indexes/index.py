"""
@author: Nicklas Ansman-Giertz
@contact: U{ngiertz@splunk.com<mailto:ngiertz@splunk.com>}
@since: 2011-11-23
"""
from abc import abstractmethod

from pytest_splunk_addon.helmut.manager.object import ItemFromManager


class Index(ItemFromManager):
    """
    The Index class represents an index in Splunk.
    """

    @abstractmethod
    def disable(self):
        """
        Disable this index. Requires Splunk to restart.
        """
        pass

    @abstractmethod
    def enable(self):
        """
        Enable this index. Does not require Splunk to restart.
        """
        pass

    @abstractmethod
    def edit(self, **kwargs):
        """
        Edit this index. Check REST documentation to see what options are
        available at
        http://docs.splunk.com/Documentation/Splunk/latest/RESTAPI/RESTindex
        """
        pass
