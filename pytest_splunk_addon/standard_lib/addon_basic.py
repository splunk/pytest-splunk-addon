import logging

import pytest
import pprint

INTERVAL = 20
RETRY = 5
class Basic:
    logger = logging.getLogger()

    @pytest.mark.splunk_addon_internal_errors
    def test_splunk_internal_errors(self, splunk_search_util, record_property, caplog):
        search = """
            search index=_internal CASE(ERROR) 
            sourcetype!=splunkd_ui_access 
            AND sourcetype!=splunk_web_access 
            AND sourcetype!=splunk_web_service 
            AND sourcetype!=splunkd_access 
            AND sourcetype!=splunkd
            | table _raw"""

        result, results = splunk_search_util.checkQueryCountIsZero(search)
        if not result:
            record_property("results", results.as_list)
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(results.as_list)
        assert result == True

    # This test ensures the contained samples will produce at lease one event per sourcetype
    @pytest.mark.splunk_addon_searchtime
    def test_sourcetype(
        self, splunk_search_util, splunk_app_props, record_property, caplog
    ):
        record_property(splunk_app_props["field"], splunk_app_props["value"])
        search = f"search (index=_internal OR index=*) AND {splunk_app_props['field']}=\"{splunk_app_props['value']}\""

        # run search
        result = splunk_search_util.checkQueryCountIsGreaterThanZero(
            search, interval=10, retries=8
        )
        record_property("search", search)

        assert result == True

    @pytest.mark.splunk_addon_searchtime
    def test_sourcetype_fields(
        self, splunk_search_util, splunk_app_fields, record_property, caplog
    ):
        record_property("sourcetype", splunk_app_fields["sourcetype"])
        record_property("fields", splunk_app_fields["fields"])

        search = f"search (index=_internal OR index=*) sourcetype={splunk_app_fields['sourcetype']}"
        for f in splunk_app_fields["fields"]:
            search = search + f' AND ({f}=* AND NOT {f}="-" AND NOT {f}="")'

        # run search
        result = splunk_search_util.checkQueryCountIsGreaterThanZero(
            search, interval=10, retries=3
        )
        record_property("search", search)

        assert result == True

    @pytest.mark.splunk_addon_searchtime
    def test_sourcetype_fields_no_dash(
        self, splunk_search_util, splunk_app_fields, record_property, caplog
    ):
        record_property("sourcetype", splunk_app_fields["sourcetype"])
        record_property("fields", splunk_app_fields["fields"])

        search = f"search (index=_internal OR index=*) sourcetype={splunk_app_fields['sourcetype']} AND ("
        op = ""
        for f in splunk_app_fields["fields"]:
            search = search + f' {op} {f}="-"'
            op = "OR"
        search = search + ")"
        # run search
        result = splunk_search_util.checkQueryCountIsGreaterThanZero(
            search, interval=1, retries=1
        )
        record_property("search", search)

        assert result == False

    @pytest.mark.splunk_addon_searchtime
    def test_sourcetype_fields_no_empty(
        self, splunk_search_util, splunk_app_fields, record_property, caplog
    ):
        record_property("sourcetype", splunk_app_fields["sourcetype"])
        record_property("fields", splunk_app_fields["fields"])

        search = f"search (index=_internal OR index=*) sourcetype={splunk_app_fields['sourcetype']} AND ("
        op = ""
        for f in splunk_app_fields["fields"]:
            search = search + f' {op} {f}=""'
            op = "OR"
        search = search + ")"
        # run search
        result = splunk_search_util.checkQueryCountIsGreaterThanZero(
            search, interval=1, retries=1
        )
        record_property("search", search)

        assert result == False

    @pytest.mark.splunk_addon_searchtime
    def test_tags(self, splunk_search_util, splunk_app_tags, record_property, caplog):
        """
        Test case to check tags mentioned in tags.conf
        
        This test case checks if a tag is assigned to the event if it is enabled,
        also checks that a disabled tag is not assigned to the event if it is disabled.
        
        Args:
            splunk_search_util : A helmut_lib.SearchUtil.SearchUtil object that helps to search on Splunk.
            splunk_app_tags : pytest parameters to test.
            record_property : pytest fixture to document facts of test cases.
            caplog : fixture to capture logs. 

        """
        if splunk_app_tags.get("enabled_tag"):
            tag = splunk_app_tags["enabled_tag"]
            enabled = True
        else:
            tag = splunk_app_tags["disabled_tag"]
            enabled = False
        condition = splunk_app_tags["condition"]
        self.logger.info(f"Testing for tag {tag} with condition {condition}")
        record_property("Event_with", condition)
        record_property("tag", tag)
        record_property("enabled", enabled)

        search = f"search index=* {condition} AND tag={tag}"
        self.logger.debug(f"Search: {search}")
        result = splunk_search_util.checkQueryCountIsGreaterThanZero(
            search, interval=INTERVAL, retries=RETRY
        )
        record_property("search", search)

        assert result is enabled

    # # This test ensures the contained samples will produce at lease one event per eventtype
    # @pytest.mark.splunk_addon_searchtime
    # @flaky(max_runs=5, min_passes=1)
    # def test_basic_eventtype(self, splunk_search_util, eventtypes):
    #
    #     self.logger.debug("Testing eventtype={}", eventtypes)
    #     search = "search (index=_internal OR index=*) AND eventtype=\"{}\"".format(eventtypes)
    #
    #     # run search
    #     result = splunk_search_util.checkQueryCountIsGreaterThanZero(
    #         search,
    #         interval=1, retries=1)
    #
    #     if not result:
    #         pytest.fail(search)
    #
    # @pytest.mark.splunk_addon_searchtime
    # @flaky(max_runs=5, min_passes=1)
    # def test_fields(self, splunk_search_util, prop_elements):
    #     search = "search (index=_internal OR index=*) AND sourcetype=\"{}\" AND {}".format(
    #         prop_elements['sourcetype'],
    #         prop_elements['field']
    #     )
    #
    #     # run search
    #     result = splunk_search_util.checkQueryCountIsGreaterThanZero(
    #         search,
    #         interval=2, retries=5)
    #
    #     if not result:
    #         pytest.fail(search)
