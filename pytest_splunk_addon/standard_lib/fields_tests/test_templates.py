# -*- coding: utf-8 -*-
"""
Includes the test scenarios to check the field extractions of an Add-on.
"""
import pprint
import logging
import pytest
from ..addon_parser import Field

INTERVAL = 3
RETRIES = 3


class FieldTestTemplates(object):
    """
    Test templates to test the knowledge objects of an App
    """

    logger = logging.getLogger("pytest-splunk-addon-tests")

    @pytest.mark.splunk_searchtime_fields
    @pytest.mark.splunk_app_internal_errors
    def test_splunk_internal_errors(self, splunk_search_util, record_property, caplog):
        search = """
            search index=_internal CASE(ERROR)
            sourcetype!=splunkd_ui_access
            AND sourcetype!=splunk_web_access
            AND sourcetype!=splunk_web_service
            AND sourcetype!=splunkd_access
            AND sourcetype!=splunkd
            | table _raw
        """
        record_property("search", search)
        result, results = splunk_search_util.checkQueryCountIsZero(search)
        if not result:
            record_property("results", results.as_list)
            pp = pprint.PrettyPrinter(indent=4)
            result_str = pp.pformat(results.as_list[:10])
        assert result, (
            f"Query result greater than 0.\nsearch={search}\n"
            f"found result={result_str}"
        )

    @pytest.mark.splunk_searchtime_fields
    @pytest.mark.splunk_searchtime_fields_positive
    def test_props_fields(
        self, splunk_search_util, splunk_searchtime_fields_positive, record_property
    ):
        """
        This test case checks that a field value has the expected values.

        Args:
            splunk_search_util (SearchUtil): Object that helps to search on Splunk.
            splunk_searchtime_fields_positive (fixture): Test for stanza field.
            record_property (fixture): Document facts of test cases.
            caplog (fixture): fixture to capture logs.
        """

        # Search Query 
        record_property("stanza_name", splunk_searchtime_fields_positive["stanza"])
        record_property("stanza_type", splunk_searchtime_fields_positive["stanza_type"])
        record_property("fields", splunk_searchtime_fields_positive["fields"])

        search = (
            f"search (index=_internal OR index=*)"
            f" {splunk_searchtime_fields_positive['stanza_type']}=\""
            f"{splunk_searchtime_fields_positive['stanza']}\""
        )
        for field_dict in splunk_searchtime_fields_positive["fields"]:
            field = Field(field_dict)
            expected_values = ", ".join([f'"{each}"' for each in field.expected_values])
            negative_values = ", ".join([f'"{each}"' for each in field.negative_values])

            search = (
                search + f" AND ({field} IN ({expected_values})"
                f" AND NOT {field} IN ({negative_values}))"
            )

        self.logger.info(f"Executing the search query: {search}")

        # run search
        result = splunk_search_util.checkQueryCountIsGreaterThanZero(
            search, interval=INTERVAL, retries=RETRIES
        )
        record_property("search", search)

        assert result, (
            f"No result found for the search.\nsearch={search}\n"
            f"interval={INTERVAL}, retries={RETRIES}"
        )

    @pytest.mark.splunk_searchtime_fields
    @pytest.mark.splunk_searchtime_fields_negative
    def test_props_fields_no_dash_not_empty(
        self, splunk_search_util, splunk_searchtime_fields_negative, record_property
    ):
        """
        This test case checks negative scenario for the field value.

        Args:
            splunk_search_util (SearchUtil): 
                Object that helps to search on Splunk.
            splunk_searchtime_fields_negative (fixture): 
                Test for stanza field.
            record_property (fixture): 
                Document facts of test cases.
            caplog (fixture): 
                fixture to capture logs.
        """

        # Search Query 
        record_property("stanza_name", splunk_searchtime_fields_negative["stanza"])
        record_property("stanza_type", splunk_searchtime_fields_negative["stanza_type"])
        record_property("fields", splunk_searchtime_fields_negative["fields"])

        search = (
            f"search (index=_internal OR index=*)"
            f" {splunk_searchtime_fields_negative['stanza_type']}=\""
            f"{splunk_searchtime_fields_negative['stanza']}\""
        )

        fields_search = []
        for field_dict in splunk_searchtime_fields_negative["fields"]:
            field = Field(field_dict)
            negative_values = ", ".join([f'"{each}"' for each in field.negative_values])

            fields_search.append(f"({field} IN ({negative_values}))")
        search += " AND ({})".format(" OR ".join(fields_search))
        self.logger.info(f"Executing the search query: {search}")

        # run search
        result, results = splunk_search_util.checkQueryCountIsZero(search)
        record_property("search", search)
        if not result:
            record_property("results", results.as_list)
            pp = pprint.PrettyPrinter(indent=4)
            result_str = pp.pformat(results.as_list[:10])
        assert result, (
            f"Query result greater than 0.\nsearch={search}\n"
            f"found result={result_str}"
        )

    @pytest.mark.splunk_searchtime_fields
    @pytest.mark.splunk_searchtime_fields_tags
    def test_tags(
        self, splunk_search_util, splunk_searchtime_fields_tags, record_property, caplog
    ):
        """
        Test case to check tags mentioned in tags.conf

        This test case checks if a tag is assigned to the event if enabled,
        and also checks that a tag is not assigned to the event if disabled.

        Args:
            splunk_search_util (helmut_lib.SearchUtil.SearchUtil): 
                object that helps to search on Splunk.
            splunk_searchtime_fields_tags (fixture): pytest parameters to test.
            record_property (fixture): pytest fixture to document facts of test cases.
            caplog (fixture): fixture to capture logs.
        """

        is_tag_enabled = splunk_searchtime_fields_tags.get("enabled", True)
        tag_query = splunk_searchtime_fields_tags["stanza"]
        tag = splunk_searchtime_fields_tags["tag"]
        self.logger.info(f"Testing for tag {tag} with tag_query {tag_query}")

        record_property("Event_with", tag_query)
        record_property("tag", tag)
        record_property("is_tag_enabled", is_tag_enabled)

        search = f"search (index=* OR index=_internal) {tag_query} AND tag={tag}"
        self.logger.info(f"Search: {search}")

        result = splunk_search_util.checkQueryCountIsGreaterThanZero(
            search, interval=INTERVAL, retries=RETRIES
        )

        record_property("search", search)

        if is_tag_enabled:
            assert result, (
                f"No events found for the enabled Tag={tag}."
                f"\nsearch={search}"
                f"\ninterval={INTERVAL}, retries={RETRIES}"
            )
        else:
            assert not result, (
                f"Events found for the disabled Tag={tag}."
                f"\nsearch={search}"
                f"\ninterval={INTERVAL}, retries={RETRIES}"
            )

    @pytest.mark.splunk_searchtime_fields
    @pytest.mark.splunk_searchtime_fields_eventtypes
    def test_eventtype(
        self,
        splunk_search_util,
        splunk_searchtime_fields_eventtypes,
        record_property,
        caplog,
    ):
        """
        Tests if all eventtypes in eventtypes.conf are generated in Splunk.
        Args:
            splunk_search_util (fixture): 
                Fixture to create a simple connection to Splunk via SplunkSDK
            splunk_searchtime_fields_eventtypes (fixture): 
                Fixture containing list of eventtypes
            record_property (fixture): 
                Used to add user properties to test report
            caplog (fixture): 
                Access and control log capturing
        Returns:
            Asserts whether test case passes or fails.
        """
        record_property(
            "eventtype", splunk_searchtime_fields_eventtypes["stanza"]
        )
        search = (f"search (index=_internal OR index=*) AND "
                  f"eventtype="
                  f"\"{splunk_searchtime_fields_eventtypes['stanza']}\"")

        self.logger.info(
            "Testing eventtype =%s", splunk_searchtime_fields_eventtypes["stanza"]
        )

        self.logger.info("Search query for testing =%s", search)

        # run search
        result = splunk_search_util.checkQueryCountIsGreaterThanZero(
            search, interval=INTERVAL, retries=RETRIES
        )
        record_property("search", search)
        assert result, (
            f"No result found for the search.\nsearch={search}\n"
            f"interval={INTERVAL}, retries={RETRIES}"
        )
