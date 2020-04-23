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
        """
        Test the the required fields in the data models are extracted with valid values. 
        Supports 3 scenarios. The test order is maintained for better test report.
        1. Check that there is at least 1 event mapped with the data model 
        2. Check that each required field is extracted in all of the events mapped with the data model.
        3. Check that if there are inter dependent fields, either all fields should be extracted or 
            none of them should be extracted.
        """

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

        # All assertion are made in the same tests to make the test report with
        # very clear order of scenarios. with this approach, a user will be able to identify 
        # what went wrong very quickly.
        assert all([each_result["event_count"] > 0 
            for each_result in result.values()
        ]), (
            "0 Events found in at least one sourcetype mapped with the dataset."
            f"\n{test_helper.format_exc_message()}"
        )
        if len(splunk_app_cim_fields["fields"]) == 1:
            test_field = splunk_app_cim_fields["fields"][0].name
            assert all([
                each_field["field_count"] > 0
                for each_result in result.values()
                for each_field in each_result["fields"]
            ]), (
                    f"Field {test_field} not extracted in any events."
                    f"\n{test_helper.format_exc_message()}"
                )
            assert all([
                each_field["field_count"] == each_field["valid_field_count"]
                for each_result in result.values()
                for each_field in each_result["fields"]
                ]), (
                f"Field {test_field} have invalid values."
                f"\n{test_helper.format_exc_message()}"
            )
        elif len(splunk_app_cim_fields["fields"]) > 1:
            # Check that count for all the fields in cluster is same. 
            # If all the fields are not extracted in an event, that's a passing scenario
            # The count of the field may or may not be same with the count of event. 
            field_list = [
                    each_field["field_count"] 
                    for each_result in result.values()
                    for each_field in each_result["fields"]
                ] + [
                    each_field["valid_field_count"] 
                    for each_result in result.values()
                    for each_field in each_result["fields"]
                ]
            assert len(set(field_list)) == 1, (
                    "All fields from the field-cluster should be extracted with valid values if any one field is extracted."
                    f"\n{test_helper.format_exc_message()}"
            )

