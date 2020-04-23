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

    @pytest.mark.splunk_app_cim
    @pytest.mark.splunk_app_cim_fields
    def test_cim_required_fields(
        self, splunk_search_util, splunk_app_cim_fields, record_property
    ):

        # Search Query 
        base_search = "search "
        for each_set in splunk_app_cim_fields["data_set"]:
            base_search += " ({})".format(each_set.search_constraints)

        base_search += " AND ({})".format(
            splunk_app_cim_fields["tag_stanza"]
        )

        test_helper = FieldTestHelper(
            splunk_search_util, 
            splunk_app_cim_fields["fields"],
            interval=INTERVAL, retries=RETRIES
        )

        # Execute the query and get the results 
        result = test_helper.test_field(base_search)
        record_property("search", test_helper.search)

        assert result["event_count"] > 0, (
            "0 Events found."
            f"\n{test_helper.format_exc_message()}"
        )
        if len(result["fields"]) == 1:
            test_field = result["fields"][0]
            assert test_field["field_count"] > 0, (
                    f"Field {test_field['field']} not extracted in any events"
                    f"\n{test_helper.format_exc_message()}"
                )
            assert test_field["field_count"] == test_field["valid_field_count"], (
                f"Field {test_field['field']} have invalid values={test_field['invalid_values'][:10]}"
                f"\n{test_helper.format_exc_message()}"
            )
        elif len(result["fields"]) > 1:
            field_list = [
                    each_field["field_count"] for each_field in result["fields"]
                ] + [
                    each_field["valid_field_count"] for each_field in result["fields"]
                ]
            assert len(set(field_list)) == 1, (
                    "All fields from the field-cluster should be extracted with valid values if any one field is extracted."
                    f"\n{test_helper.format_exc_message()}"
            )

