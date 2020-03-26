import logging

import pytest
import pprint


class Basic:
    LOGGER = logging.getLogger()

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
    def test_sourcetype(self, splunk_search_util, splunk_app_props, record_property, caplog):
        """
        Test case to check props stanza mentioned in props.conf
        
        This test case checks props stanza is not empty, blank and dash value.
        Args:
            splunk_search_util(helmut_lib.SearchUtil.SearchUtil): Object that helps to search on Splunk.
            splunk_props_fields(fixture): Test for stanza.
            record_property(fixture):  Document facts of test cases.
            caplog : fixture to capture logs. 
        """
        record_property(splunk_app_props["field"], splunk_app_props["value"])
        search = f"search (index=_internal OR index=*) AND {splunk_app_props['field']}=\"{splunk_app_props['value']}\""
        self.LOGGER.debug(f"Executing the search query: {search}")
        # run search
        result = splunk_search_util.checkQueryCountIsGreaterThanZero(
            search, interval=10, retries=8
        )
        record_property("search", search)

        assert result == True

    @pytest.mark.splunk_addon_searchtime
    def test_sourcetype_fields(self, splunk_search_util, splunk_app_fields, record_property, caplog):
        """
        Test case to check props property mentioned in props.conf
        
        This test case checks props field is not empty, blank and dash value.
        Args:
            splunk_search_util(helmut_lib.SearchUtil.SearchUtil): Object that helps to search on Splunk.
            splunk_app_fields(fixture): Test for stanza field.
            record_property(fixture):  Document facts of test cases.
            caplog : fixture to capture logs. 
        """
        record_property("stanza_name", splunk_app_fields["stanza_name"])
        record_property("stanza_type", splunk_app_fields["stanza_type"])
        record_property("fields", splunk_app_fields["fields"])

        search = f"search (index=_internal OR index=*) {splunk_app_fields['stanza_type']}={splunk_app_fields['stanza_name']}"
        for f in splunk_app_fields["fields"]:
            search = search + f' AND ({f}=* AND NOT {f}="-" AND NOT {f}="")'
        
        self.LOGGER.debug(f"Executing the search query: {search}")
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
