# ****************
# Tests (Using splunk search util)
#   a)Check for data model mapping
#   b)Check for field mappings in the requirement files and the extracted events in Splunk


class ReqsTestTemplates(object):
    """
    Test templates to test the log files in the event_analytics folder
    """

    def test_cim_params(self, splunk_searchtime_requirement_param, splunk_search_util):
        """
        Test to check if model and field value pairs given in the SME requirement file match with the one's extracted in Splunk
        Gives proper messaging for test failures and failure field value pairs

        Args:
            splunk_searchtime_requirement_param: Will contain event,
                        model and key value pair for field names and values.
            splunk_search_util: used to run searches and get search results
        """
        pass
