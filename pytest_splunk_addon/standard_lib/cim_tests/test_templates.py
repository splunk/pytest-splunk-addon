# -*- coding: utf-8 -*-
"""
Includes the test scenarios to check the CIM compatibility of an Add-on.
"""
import logging
import pytest
from ..fields_tests.field_test_helper import FieldTestHelper

INTERVAL = 3
RETRIES = 3


class CIMTestTemplates(object):
    """
    Test scenarios to check the CIM compatibility of an Add-on 
    Supported Test scenarios:
        - The eventtype should exctract all required fields of data model 
        - One eventtype should not be mapped with more than one data model 
        - Field Cluster should be verified (should be included with required field test)
        - Verify if CIM installed or not 
        - Not Allowed Fields should not be extracted 
        - TODO 
    """

    logger = logging.getLogger("pytest-splunk-addon-cim-tests")

    @pytest.mark.splunk_addon_cim
    def test_cim_required_fields(
        self, splunk_search_util, splunk_app_cim, record_property
    ):

        # Search Query
        base_search = "search "
        for each_set in splunk_app_cim["data_set"]:
            base_search += " ({})".format(each_set.search_constraints)

        base_search += " AND ({})".format(splunk_app_cim["tag_stanza"])

        test_helper = FieldTestHelper(
            splunk_search_util,
            splunk_app_cim["fields"],
            interval=INTERVAL,
            retries=RETRIES,
        )

        # Execute the query and get the results
        result = test_helper.test_field(base_search)

        assert result["event_count"] > 0, (
            "0 Events found." f"\n{test_helper.get_exc_message()}"
        )

        if "fields" in result:
            assert all(
                [each_field["field_count"] > 0 for each_field in result["fields"]]
            ), (
                "Fields are not extracted in any events."
                f"\n{test_helper.get_exc_message()}"
            )
            assert all(
                [
                    each_field["field_count"] == each_field["valid_field_count"]
                    for each_field in result["fields"]
                ]
            ), ("Fields do not have valid values." f"\n{test_helper.get_exc_message()}")

        record_property("search", test_helper.search)
