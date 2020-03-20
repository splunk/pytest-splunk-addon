"""
@author: Nicklas Ansman-Giertz
@contact: U{ngiertz@splunk.com<mailto:ngiertz@splunk.com>}
@since: 2011-11-23
"""

from abc import ABCMeta, abstractmethod
from builtins import object

from future.utils import with_metaclass


class Collection(with_metaclass(ABCMeta, object)):
    """
    A Collection metaclass that specifies what functions a collection in the
    Helmut framework must implement.
    """

    def __call__(self):
        return list(self.items())

    def __len__(self):
        return len(list(self.items()))

    def __iter__(self):
        for item in list(self.items()):
            yield item

    @abstractmethod
    def items(self):
        """
        Return a collection of all the contained objects. It is up to the
        subclass to decide whether this collection is a list, map or of any
        other kind.

        @return: A collection of all the items contained.
        """
        pass

    @abstractmethod
    def __contains__(self, item):
        """
        Return boolean whether item is contained in Collection.

        @param item: The item which is checked if contained.
        """
        pass
