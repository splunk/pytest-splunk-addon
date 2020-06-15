import logging


class IndexTimeTestTemplate(object):

    logger = logging.getLogger("pytest-splunk-addon-tests")

    def test_index_time_extractions(
        self, splunk_search_util, record_property, caplog
    ):

        # implementation here
        assert True
