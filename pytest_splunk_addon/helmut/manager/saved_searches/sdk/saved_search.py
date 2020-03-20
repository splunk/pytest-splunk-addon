from pytest_splunk_addon.helmut.manager.jobs.sdk import SDKJobWrapper
from pytest_splunk_addon.helmut.manager.saved_searches.saved_search import SavedSearch


class SDKSavedSearchWrapper(SavedSearch):
    """
    The L{SavedSearch} subclass corresponding to an SavedSearch object in the
    Splunk Python SDK.
    """

    def __init__(self, sdk_connector, sdk_saved_search):
        """
        SDKSavedSearchWrapper's constructor.

        @param sdk_connector: The connector which talks to Splunk through the
                              Splunk Python SDK.
        @type sdk_connector: SDKConnector
        @param sdk_saved_search: The name of the new saved search.
        @type sdk_saved_search: String
        """
        super(SDKSavedSearchWrapper, self).__init__(sdk_connector)
        self._raw_sdk_saved_search = sdk_saved_search

    def run(self, **kwargs):
        """
        Run this saved search.
        @param **kwargs: Any other settings for running this saved search.
        @type **kwargs: Dictionary
        """
        self.logger.info("Running saved search %s" % self.name)
        return SDKJobWrapper(
            self.connector, self._raw_sdk_saved_search.dispatch(**kwargs)
        )

    def edit(self, query=None, **kwargs):
        """
        Edit this saved search.
        @param query: The query that this saved search is supposed to run.  Remains unchanged if no value is given.
        @type query: String
        @param **kwargs: Any other settings for the saved search.
        @type **kwargs: Dictionary
        """
        self.logger.info("Editing saved search %s" % self.name)
        self._raw_sdk_saved_search.update(query, **kwargs)

    def disable(self):
        """
        Disable this saved search.
        """
        self.logger.info("Disabling saved search %s" % self.name)
        self._raw_sdk_saved_search.disable()

    def delete(self):
        """
        Delete this saved search.
        """
        self.logger.info("Deleting saved search %s" % self.name)
        self._raw_sdk_saved_search.delete()

    def enable(self):
        """
        Enable this saved search.
        """
        self.logger.info("Enabling saved search %s" % self.name)
        self._raw_sdk_saved_search.enable()

    def get_artifacts(self):
        """
        Return the artifacts associated with this saved search.
        """
        results = self._raw_sdk_saved_search.history()
        jobs = []
        for result in results:
            job = SDKJobWrapper(self.connector, result)
            jobs.append(job)
        return jobs

    @property
    def name(self):
        """
        The name of the saved_search.
        """
        return self._raw_sdk_saved_search.name

    @property
    def content(self):
        """
        The contents of the saved_search.
        """
        return self._raw_sdk_saved_search.content
