"""
@author: Nicklas Ansman-Giertz
@contact: U{ngiertz@splunk.com<mailto:ngiertz@splunk.com>}
@since: 2011-11-23
"""
import copy
from builtins import object


class Results(object):
    """
    A class that represents a result set.

    These results can be represented in two ways; as a list or as a dictionary.

    The formats are:

    List::
        [
            {
                'field1': value1,
                'field2': value2,
                ...
            },

            {
                'field2': value3,
                'field3': value4,
                ...
            }
        ]

    Dictionary::
        {
            'field1': [value1, None, ...],
            'field2': [value2, value3, ...],
            'field3': [None, value4, ...],
            ...
        }

    As you can see each event in the list doesn't have to contain all fields.

    @ivar _list: The results as a list
    @ivar _dict_cached: Since creating the dictionary is expensive it's cached.
                        You should use the _dict property though!
    """

    def __init__(self, results_):
        """
        Constructor

        @param results_: The raw results as returned by ResultReader
        @type results_: list
        """
        super(Results, self).__init__()

        self._list = results_
        self._dict_cache = None

    def __repr__(self):
        """
        Returns a string representation of this object

        @return: The representation
        @rtype: str
        """
        return "Results set with {count} result(s)".format(count=len(self))

    def get_field(self, field):
        """
        Returns the values for the specified field or None if it doesn't exist

        @param field: The field to get
        @type field: str
        @return: A list of values for that field
        @rtype: list(str)
        """
        return self.as_dict.get(field)

    def __getitem__(self, index):
        """
        Returns the specified event as a dictionary.

        used when doing this:
            >>> results[index]

        @param index: The index to get
        @type index: int
        @return: The fields for that event
        @rtype: dict(str: str)
        """
        return self.as_list[index]

    def get_event(self, index):
        """
        Returns the event at the specified index as a dictionary

        This is an alias for C{__getitem__}

        @param index: The index to get
        @type index: int
        @return: The event at that index
        @rtype: dict(str: str)
        """
        return self[index]

    def __iter__(self):
        """
        Returns an iterator for this result set.

        The iterator will iterate over each event.

        This is used when doing
            >>> for event in results: ...

        @return: The iterator
        @rtype: iterator
        """
        return self.as_list.__iter__()

    def __contains__(self, field):
        """
        Checks if the specified field is in this result set.

        This is equal to doing C{field in results.as_dict}

        @param field: The field to check
        @type field: str
        @return: True if it exists
        @rtype: bool
        """
        return field in self._dict

    def __len__(self):
        """
        Returns the number of events in this result set

        @return: The event count
        @rtype: int
        """
        return len(self._list)

    @property
    def as_dict(self):
        """
        This result set as a dictionary. The format is specified in the
        documentation for the class.

        This is a copy of the results so you can do whatever you want to do with
        it.

        @rtype: dict
        """
        return copy.deepcopy(self._dict)

    @property
    def as_list(self):
        """
        This result set as a list. The format is specified in the documentation
        for the class

        This is a copy of the results so you can do whatever you want to do with
        it.

        @rtype: list
        """
        return copy.deepcopy(self._list)

    @property
    def fields(self):
        """
        The fields in this result set as a list.

        This is a copy of the fields so you can do whatever you want to do with
        it.

        @rtype: list
        """
        return list(self._dict.keys())

    @property
    def _dict(self):
        """
        Returns the results as a dictionary.

        It caches the results so that the second call is very fast

        @rtype: dict
        """
        if not self._dict_cache:
            self._dict_cache = _list_to_dictionary(self._list)
        return self._dict_cache


def _list_to_dictionary(events):
    """
    Converts a list of events to a dictionary of fields.

    Input format::
        [
            {
                'field1': value1,
                'field2': value2,
                ...
            },

            {
                'field2': value3,
                'field3': value4,
                ...
            },

            ...
        ]

    Output format::
        {
            'field1': [value1, None, ...],
            'field2': [value2, value3, ...],
            'field3': [None, value4, ...],
            ...
        }

    If not all fields are present in every event None will be inserted instead.

    @param events: The events as a list of dictionaries
    @type events: list(dict(field(str): value(str)))

    @return: The events as a dictionary.
    @rtype: dict(field(str): values(list(str)))
    """
    fields = _get_fields(events)
    r = {}
    for event in events:
        for field in fields:
            if not field in r:
                r[field] = []
            r[field].append(event.get(field, None))
    return r


def _get_fields(events):
    """
    Returns a list of all fields in the given event set.

    @param events: The events as a list of dictionaries.
    @type events: list(dict(str: str))
    @return: All the fields.
    @rtype: set(str)
    """
    fields = set()
    for event in events:
        fields.update(list(event.keys()))
    return fields
