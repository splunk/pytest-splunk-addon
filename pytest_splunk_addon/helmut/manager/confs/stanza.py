"""
@author: Nicklas Ansman-Giertz
@contact: U{ngiertz@splunk.com<mailto:ngiertz@splunk.com>}
@since: 2011-11-23
"""

from abc import abstractmethod

from pytest_splunk_addon.helmut.manager.object import ItemFromManager
from pytest_splunk_addon.helmut.misc.collection import Collection


class Stanza(ItemFromManager, Collection):
    """
    This class is a collection of key-value pairs contained in a stanza.

    See L{Confs} and L{Conf} for more information.
    """

    def __init__(self, conf, stanza_name):
        """
        The constructor for Stanza.

        @param conf: The Conf object which contains this Stanza object.
        @type conf: L{Conf}
        @param stanza_name: The name of this stanza.
        @type type: String
        """
        ItemFromManager.__init__(self, conf.connector)
        Collection.__init__(self)

        self._conf = conf
        self._name = stanza_name

    @property
    def conf(self):
        return self._conf

    @property
    def conf_name(self):
        return self.conf.name

    @property
    def name(self):
        return self._name

    @abstractmethod
    def items(self):
        pass

    @abstractmethod
    def __setitem__(self, key, value):
        pass

    @abstractmethod
    def delete_value(self, value):
        """
        Delete a value from the stanza.

        @param value: The attributes name to remove (i.e the key of
                          the key-value pair).
        @type value: String.
        @return: A Boolean True if the key is now None or '', False otherwise.
        @rtype - Boolean
        """
        pass

    def __getitem__(self, key):
        """
        Fetch a value in the stanza.

        @param key: The key associated with the value to be fetched.
        @type key: String
        """
        #        print "fetching key> %s"%key
        for (k, v) in self:
            #            print "key %s val %s"%(k, v)
            if key == k:
                return v
        raise KeyError("The specified key is not in the stanza")

    def __contains__(self, key):
        return key in list(self.items())

    def __iter__(self):
        return list(self.items()).iteritems()
