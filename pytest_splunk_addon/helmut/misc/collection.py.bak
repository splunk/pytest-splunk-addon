'''
@author: Nicklas Ansman-Giertz
@contact: U{ngiertz@splunk.com<mailto:ngiertz@splunk.com>}
@since: 2011-11-23
'''

from abc import ABCMeta, abstractmethod


class Collection(object):
    '''
    A Collection metaclass that specifies what functions a collection in the
    Helmut framework must implement.
    '''
    __metaclass__ = ABCMeta

    def __call__(self):
        return self.items()

    def __len__(self):
        return len(self.items())

    def __iter__(self):
        for item in self.items():
            yield item

    @abstractmethod
    def items(self):
        '''
        Return a collection of all the contained objects. It is up to the
        subclass to decide whether this collection is a list, map or of any
        other kind.

        @return: A collection of all the items contained.
        '''
        pass

    @abstractmethod
    def __contains__(self, item):
        '''
        Return boolean whether item is contained in Collection.

        @param item: The item which is checked if contained.
        '''
        pass
