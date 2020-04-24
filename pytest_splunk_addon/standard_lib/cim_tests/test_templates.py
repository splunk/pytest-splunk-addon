# -*- coding: utf-8 -*-
"""
Includes the test scenarios to check the CIM compatibility of an Add-on.
"""
import logging
import pytest
from .field_test_helper import FieldTestHelper

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

        base_search += " AND ({})".format(splunk_app_cim_fields["tag_stanza"])

        test_helper = FieldTestHelper(
            splunk_search_util,
            splunk_app_cim_fields["fields"],
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

    @pytest.mark.splunk_app_cim
    @pytest.mark.splunk_app_cim_fields_not_extracted
    def test_cim_not_extracted_fields(
        self, splunk_search_util, splunk_app_cim_fields_not_extracted, record_property
    ):
        # Search Query
        base_search = "search"
        for each_set in splunk_app_cim_fields_not_extracted["data_set"]:
            base_search += " ({})".format(each_set.search_constraints)

        base_search += " AND ({}) ".format(
            splunk_app_cim_fields_not_extracted["tag_stanza"]
        )

        base_search += " AND ("
        for each_field in splunk_app_cim_fields_not_extracted["fields"]:
            base_search += " ({}=*) OR".format(each_field.name)

        base_search = base_search[:-2]
        base_search += ")"

        if not splunk_app_cim_fields_not_extracted["tag_stanza"]:
            base_search = base_search.replace("search OR", "search")

        base_search += " | stats "

        for each_field in splunk_app_cim_fields_not_extracted["fields"]:
            base_search += " count({fname}) AS {fname}".format(fname=each_field.name)

        base_search += " by sourcetype"
        record_property("search", base_search)

        result, results = splunk_search_util.checkQueryCountIsZero(
            base_search, interval=INTERVAL, retries=RETRIES
        )

        violations = []
        if results:
            violations = [
                {
                    "sourcetype": each_elem["sourcetype"],
                    "field": field,
                    "event_count": each_elem.get(field),
                }
                for each_elem in results.as_list
                for field in results.fields
                if not each_elem.get(field) == "0"
                and not each_elem.get(field) == each_elem["sourcetype"]
            ]
            violation_str = (
                "\n These fields are automatically provided by asset and identity"
                " correlation features of applications like Splunk Enterprise Security."
                "\n Do not define extractions for these fields when writing add-ons.\n"
                " Expected eventcount: 0 \n"
            )
            violation_str += FieldTestHelper.get_table_output(
                headers=["Sourcetype", "Fields", "Event Count"],
                value_list=[
                    [
                        each_violation["sourcetype"],
                        each_violation["field"],
                        each_violation["event_count"],
                    ]
                    for each_violation in violations
                ],
            )

        assert not violations, violation_str

    @pytest.mark.splunk_app_cim
    @pytest.mark.splunk_app_cim_fields_not_allowed
    def test_cim_not_allowed_fields(
        self, splunk_app_cim_fields_not_allowed, record_property
    ):
        result_str = (
            "\n These fields are automatically provided by asset and identity"
            " correlation features of applications like Splunk Enterprise Security."
            "\n Do not define extractions for these fields when writing add-ons.\n"
        )

        result_str += FieldTestHelper.get_table_output(
            headers=["Stanza", "Classname", "Fieldname"],
            value_list=[
                [data["stanza"], data["classname"], data["name"]]
                for data in splunk_app_cim_fields_not_allowed["fields"]
            ],
        )

        assert not splunk_app_cim_fields_not_allowed["fields"], result_str
