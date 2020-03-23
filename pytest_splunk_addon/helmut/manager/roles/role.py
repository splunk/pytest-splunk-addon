"""
@author: Nicklas Ansman-Giertz
@contact: U{ngiertz@splunk.com<mailto:ngiertz@splunk.com>}
@since: 2011-11-23
"""
from abc import abstractmethod

from pytest_splunk_addon.helmut.manager.object import ItemFromManager


class Role(ItemFromManager):
    """
    The Role class represents an role in Splunk.
    """

    @abstractmethod
    def edit(self, **kwargs):
        """
        Edit this role. Check REST documentation to see what options are
        available at
        http://docs.splunk.com/Documentation/Splunk/latest/RESTAPI/RESTrole
        """
        pass
