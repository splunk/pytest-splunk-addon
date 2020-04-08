import pprint
import logging
import pytest
INTERVAL = 1
RETRIES = 1
# CIM Testing 

def temp_writer(msg):
    with open("mylogger.log", "a") as fff:
        fff.write(str(msg) + "\n")

class Basic:
    logger = logging.getLogger()


    def test_cim_fields(self):
        # Search query
        query = "tag = A AND field=*"
        assert query 

    def test_cim_only_one_model(self):
        # List the data models mapped for a tags.conf stanza 
        # Fail if it has more than one mapped. 
        pass

    @pytest.mark.splunk_addon_internal_errors
    def test_splunk_internal_errors(
        self, splunk_search_util, record_property, caplog
    ):
        search = """
            search index=_internal CASE(ERROR)
            sourcetype!=splunkd_ui_access
            AND sourcetype!=splunk_web_access
            AND sourcetype!=splunk_web_service
            AND sourcetype!=splunkd_access
            AND sourcetype!=splunkd
            | table _raw
        """
        # return
        result, results = splunk_search_util.checkQueryCountIsZero(search)
        if not result:
            record_property("results", results.as_list)
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(results.as_list)
        assert result


# Field testing 
    @pytest.mark.splunk_addon_searchtime
    def test_props_fields_positive(
            self, splunk_search_util, splunk_app_positive_fields, record_property, request
        ):
        """
        Test case to check props property mentioned in props.conf

        This test case checks props field is not empty, blank and dash value.
        Args:
            splunk_search_util(SearchUtil):
                Object that helps to search on Splunk.
            splunk_app_fields(fixture):
                Test for stanza field.
            record_property(fixture):
                Document facts of test cases.
            caplog :
                fixture to capture logs.
        """

        # Search Query 
        record_property("stanza_name", splunk_app_positive_fields["stanza"])
        record_property("stanza_type", splunk_app_positive_fields["stanza_type"])
        record_property("fields", splunk_app_positive_fields["fields"])

        search = (
            f"search (index=_internal OR index=*)"
            f" {splunk_app_positive_fields['stanza_type']}=\""
            f"{splunk_app_positive_fields['stanza']}\""
        )
        for field in splunk_app_positive_fields["fields"]:
            positive_values = ", ".join([f'"{each}"' for each in field.positive_values])
            negative_values = ", ".join([f'"{each}"' for each in field.negative_values])

            search = (search + f' AND ({field} IN ({positive_values})'
             f' AND NOT {field} IN ({negative_values}))')

        self.logger.debug(f"Executing the search query: {search}")
        temp_writer(request.node.name)
        temp_writer(search)
        temp_writer("")

        # return 
        # run search
        result = splunk_search_util.checkQueryCountIsGreaterThanZero(
            search, interval=INTERVAL, retries=RETRIES
        )
        record_property("search", search)

        assert result
    

    @pytest.mark.splunk_addon_searchtime
    def test_props_fields_negative(
            self, splunk_search_util, splunk_app_negative_fields, record_property, request
        ):

        # Search Query 
        record_property("stanza_name", splunk_app_negative_fields["stanza"])
        record_property("stanza_type", splunk_app_negative_fields["stanza_type"])
        record_property("fields", splunk_app_negative_fields["fields"])

        search = (
            f"search (index=_internal OR index=*)"
            f" {splunk_app_negative_fields['stanza_type']}=\""
            f"{splunk_app_negative_fields['stanza']}\""
        )

        for field in splunk_app_negative_fields["fields"]:
            negative_values = ", ".join([f'"{each}"' for each in field.negative_values])

            search = (search + f' AND ({field} IN ({negative_values}))')

        temp_writer(request.node.name)
        temp_writer(search)
        temp_writer("")
        # return

        self.logger.debug(f"Executing the search query: {search}")

        # run search
        result, results = splunk_search_util.checkQueryCountIsZero(
            search
        )
        record_property("search", search)
        if not result:
            record_property("results", results.as_list)
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(results.as_list)
        assert result

    # This test will check if there is at least one event with specified tags
    @pytest.mark.splunk_addon_searchtime
    def test_tags(
        self, splunk_search_util, splunk_app_tags, record_property, caplog, request
    ):
        """
        Test case to check tags mentioned in tags.conf

        This test case checks if a tag is assigned to the event if enabled,
        and also checks that a tag is not assigned to the event if disabled.

        Args:
            splunk_search_util : A helmut_lib.SearchUtil.SearchUtil object that
                helps to search on Splunk.
            splunk_app_tags : pytest parameters to test.
            record_property : pytest fixture to document facts of test cases.
            caplog : fixture to capture logs.
        """

        is_tag_enabled = splunk_app_tags.get("enabled", True)
        tag_query = splunk_app_tags["stanza"]
        tag = splunk_app_tags["tag"]
        self.logger.info(f"Testing for tag {tag} with tag_query {tag_query}")

        record_property("Event_with", tag_query)
        record_property("tag", tag)
        record_property("is_tag_enabled", is_tag_enabled)

        search = (
            f"search (index=* OR index=_internal) {tag_query} AND tag={tag}"
        )
        self.logger.debug(f"Search: {search}")
        temp_writer(request.node.name)
        temp_writer(search)
        temp_writer("")

        # return 


        result = splunk_search_util.checkQueryCountIsGreaterThanZero(
            search, interval=INTERVAL, retries=RETRIES
        )

        record_property("search", search)

        assert result is is_tag_enabled

    @pytest.mark.splunk_addon_searchtime
    def test_eventtype(
        self,
        splunk_search_util,
        splunk_app_eventtypes,
        record_property,
        caplog,
        request
    ):
        """
        Tests if all eventtypes in eventtypes.conf are generated in Splunk.
        Args:
            splunk_search_util:
                Fixture to create a simple connection to Splunk via SplunkSDK
            splunk_app_eventtypes:
                Fixture containing list of eventtypes
            record_property:
                Used to add user properties to test report
            caplog:
                Access and control log capturing
        Returns:
            Asserts whether test case passes or fails.
        """
        record_property(
            "eventtype", splunk_app_eventtypes["stanza"]
        )
        search = (f"search (index=_internal OR index=*) AND "
                  f"eventtype="
                  f"\"{splunk_app_eventtypes['stanza']}\"")

        self.logger.info(
            "Testing eventtype =%s", splunk_app_eventtypes["stanza"]
        )

        self.logger.debug("Search query for testing =%s", search)
        temp_writer(request.node.name)
        temp_writer(search)
        temp_writer("")
        # return 


        # run search
        result = splunk_search_util.checkQueryCountIsGreaterThanZero(
            search, interval=INTERVAL, retries=RETRIES
        )
        record_property("search", search)
        assert result
