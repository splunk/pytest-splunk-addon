# -*- coding: utf-8 -*-
import logging

import pytest
import pprint

INTERVAL = 3
RETRIES = 3


class Basic:
    logger = logging.getLogger()

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

        result, results = splunk_search_util.checkQueryCountIsZero(search)
        if not result:
            record_property("results", results.as_list)
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(results.as_list)
        assert result

    # This test ensures the contained samples will produce
    # at lease one event per sourcetype/source
    @pytest.mark.splunk_addon_searchtime
    def test_props_stanza(
        self, splunk_search_util, splunk_app_props, record_property, caplog
    ):
        """
        Test case to check props stanza mentioned in props.conf

        This test case checks props stanza is not empty, blank and dash value.
        Args:
            splunk_search_util(SearchUtil):
                Object that helps to search on Splunk.
            splunk_props_fields(fixture):
                Test for stanza.
            record_property(fixture):
                Document facts of test cases.
            caplog :
                fixture to capture logs.
        """

        record_property(splunk_app_props["field"], splunk_app_props["value"])
        search = (
            f"search (index=_internal OR index=*) AND "
            f"{splunk_app_props['field']}="
            f"\"{splunk_app_props['value']}\""
        )
        self.logger.debug(f"Executing the search query: {search}")
        # run search
        result = splunk_search_util.checkQueryCountIsGreaterThanZero(
            search, interval=INTERVAL, retries=RETRIES
        )
        record_property("search", search)

        assert result

    @pytest.mark.splunk_addon_searchtime
    def test_props_fields(
        self, splunk_search_util, splunk_app_fields, record_property, caplog
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
        record_property("stanza_name", splunk_app_fields["stanza_name"])
        record_property("stanza_type", splunk_app_fields["stanza_type"])
        record_property("fields", splunk_app_fields["fields"])

        search = (
            f"search (index=_internal OR index=*)"
            f" {splunk_app_fields['stanza_type']}="
            f"{splunk_app_fields['stanza_name']}"
        )
        for field in splunk_app_fields["fields"]:
            search = search + f' AND ({field}=* AND NOT {field}="-" AND NOT {field}="")'

        self.logger.debug(f"Executing the search query: {search}")
        # run search
        result = splunk_search_util.checkQueryCountIsGreaterThanZero(
            search, interval=INTERVAL, retries=RETRIES
        )
        record_property("search", search)

        assert result

    @pytest.mark.splunk_addon_searchtime
    def test_props_fields_no_dash_not_empty(
        self, splunk_search_util, splunk_app_fields, record_property, caplog
    ):
        """
        Test case to check props property mentioned in props.conf

        This test case checks negative scenario for field dash value.
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
        record_property("stanza_name", splunk_app_fields["stanza_name"])
        record_property("stanza_type", splunk_app_fields["stanza_type"])
        record_property("fields", splunk_app_fields["fields"])

        search = (
            f"search (index=_internal OR index=*)"
            f" {splunk_app_fields['stanza_type']}="
            f"{splunk_app_fields['stanza_name']} AND "
        )
        operator = ""
        for field in splunk_app_fields["fields"]:
            search = search + f'{operator} ( {field}="-" OR {field}="") '
            operator = "OR"

        self.logger.debug(f"Executing the search query: {search}")
        # run search
        result, results = splunk_search_util.checkQueryCountIsZero(search)

        if not result:
            record_property("results", results.as_list)
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(results.as_list[-10:])      
        record_property("search", search)
        assert result


    # This test will check if there is at least one event with specified tags
    @pytest.mark.splunk_addon_searchtime
    def test_tags(
        self, splunk_search_util, splunk_app_tags, record_property, caplog
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

        if splunk_app_tags.get("enabled_tag"):
            tag = splunk_app_tags["enabled_tag"]
            is_tag_enabled = True
        else:
            tag = splunk_app_tags["disabled_tag"]
            is_tag_enabled = False

        tag_query = splunk_app_tags["tag_query"]
        self.logger.info(f"Testing for tag {tag} with tag_query {tag_query}")

        record_property("Event_with", tag_query)
        record_property("tag", tag)
        record_property("is_tag_enabled", is_tag_enabled)

        search = (
            f"search (index=* OR index=_internal) {tag_query} AND tag={tag}"
        )
        self.logger.debug(f"Search: {search}")

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
            splunk_app_eventtypes["field"], splunk_app_eventtypes["value"]
        )
        search = (f"search (index=_internal OR index=*) AND "
                  f"{splunk_app_eventtypes['field']}="
                  f"\"{splunk_app_eventtypes['value']}\"")

        self.logger.info(
            "Testing eventtype =%s", splunk_app_eventtypes["value"]
        )
        self.logger.debug("Search query for testing =%s", search)

        # run search
        result = splunk_search_util.checkQueryCountIsGreaterThanZero(
            search, interval=INTERVAL, retries=RETRIES
        )
        record_property("search", search)
        assert result
