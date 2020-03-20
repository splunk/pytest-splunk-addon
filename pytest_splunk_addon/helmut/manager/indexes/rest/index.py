"""
@author: Lei Zhang
@contact: U{leiz@splunk.com<mailto:leiz@splunk.com>}
@since: 2018-06-11
"""
import time

from pytest_splunk_addon.helmut.exceptions.wait import WaitTimedOut
from pytest_splunk_addon.helmut.manager.indexes.index import Index
from pytest_splunk_addon.helmut.util.string_unicode_convert import normalize_to_unicode


class RESTIndexWrapper(Index):
    """
    The L{Index} subclass corresponding to an Index object in the
    Splunk REST API.
    """

    def __init__(self, rest_connector, rest_index):
        """
        RESTIndexWrapper's constructor.

        @param rest_connector: The connector which talks to Splunk through the
                              Splunk REST API.
        @type rest_connector: RESTConnector
        @param rest_index: The name of the new index.
        @type rest_index: String
        """
        super(RESTIndexWrapper, self).__init__(rest_connector)
        self._raw_rest_index = rest_index

    def get_total_event_count(self):
        """
        Returns the event count of the index.

        @return: The total event count.
        @rtype: int
        """
        result = self._raw_rest_index.refresh()
        return int(result["content"]["totalEventCount"])

    def wait_for_event_count(self, ecount, timeout):
        event_number = 0
        previous_event_number = 0
        counter = timeout
        done = False
        while not done and counter > 0:
            event_number = self.get_total_event_count()
            if event_number > ecount:
                self.logger.error(
                    "Index {name} contains events count is {now},more than expected events count {ecount}.".format(
                        name=self.name, now=event_number, ecount=ecount
                    )
                )
                return
            elif event_number < ecount:
                if event_number != previous_event_number:
                    self.logger.info(
                        "Index {name} events count is {now},previous events count is {pre}".format(
                            name=self.name, now=event_number, pre=previous_event_number
                        )
                    )
                    previous_event_number = event_number
                time.sleep(1)
                counter -= 1
            else:
                done = True

        if counter != 0:
            self.logger.info(
                "Indexing (%s) completed in %s seconds."
                % (self.name, (timeout - counter))
            )
        else:
            self.logger.warn(
                "Indexing (%s) did not complete within %s seconds.The events number is %s"
                % (self.name, timeout, event_number)
            )
            raise WaitTimedOut(timeout)

    def get_max_warm_db_count(self):
        """
        Returns the value for stanza field maxWarmDBCount.

        @return: The value for maxWarmDBCount.
        @rtype: int
        """
        result = self._raw_rest_index.refresh()
        return int(result["content"]["maxWarmDBCount"])

    @property
    def name(self):
        """
        The name of the index.
        """
        return self._raw_rest_index.name

    def clean(self, timeout=300):
        """
        Cleans an index. All events will be removed.

        @param timeout: The maximum time to wait for the clean in seconds.
                        Default: 300 seconds.
        @type timeout: int
        """
        self.logger.info("Cleaning index %s" % self.name)
        self._raw_rest_index.clean(timeout)

    def disable(self):
        self.logger.info("Disabling index %s" % self.name)
        self._raw_rest_index.disable()

    def enable(self):
        self.logger.info("Enabling index %s" % self.name)
        self._raw_rest_index.enable()

    def edit(self, **kwargs):
        kwargs = dict(
            [normalize_to_unicode(k), normalize_to_unicode(v)]
            for k, v in kwargs.items()
        )
        self.logger.info("Editing index %s with: %s" % (self.name, kwargs))
        self._raw_rest_index.update(**kwargs)

    def delete(self, **kwargs):
        kwargs = dict(
            [normalize_to_unicode(k), normalize_to_unicode(v)]
            for k, v in kwargs.items()
        )
        self.logger.info("Deleting index %s with: %s" % (self.name, kwargs))
        self._raw_rest_index.delete(**kwargs)
