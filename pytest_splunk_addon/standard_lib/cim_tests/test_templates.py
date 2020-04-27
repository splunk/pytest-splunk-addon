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

     @pytest.mark.splunk_searchtime_cim
    @pytest.mark.splunk_searchtime_cim_fields
    def test_cim_required_fields(
        self, splunk_search_util, splunk_searchtime_cim_fields, record_property
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
        for each_set in splunk_searchtime_cim_fields["data_set"]:
            base_search += " ({})".format(each_set.search_constraints)

        base_search += " AND ({})".format(
            splunk_searchtime_cim_fields["tag_stanza"]
        )

        test_helper = FieldTestHelper(
            splunk_search_util, 
            splunk_searchtime_cim_fields["fields"],
            interval=INTERVAL, retries=RETRIES
        )

        # Execute the query and get the results 
        results = test_helper.test_field(base_search)
        record_property("search", test_helper.search)

        # All assertion are made in the same tests to make the test report with
        # very clear order of scenarios. with this approach, a user will be able to identify 
        # what went wrong very quickly.
        assert all([each_result["event_count"] > 0 
            for each_result in results
        ]), (
            "0 Events found in at least one sourcetype mapped with the dataset."
            f"\n{test_helper.format_exc_message()}"
        )
        if len(splunk_searchtime_cim_fields["fields"]) == 1:
            test_field = splunk_searchtime_cim_fields["fields"][0].name
            assert all([
                each_field["field_count"] > 0
                for each_field in results
            ]), (
                    f"Field {test_field} not extracted in any events."
                    f"\n{test_helper.format_exc_message()}"
                )
            assert all([
                each_field["field_count"] == each_field["valid_field_count"]
                for each_field in results
                ]), (
                f"Field {test_field} have invalid values."
                f"\n{test_helper.format_exc_message()}"
            )
        elif len(splunk_searchtime_cim_fields["fields"]) > 1:
            # Check that count for all the fields in cluster is same. 
            # If all the fields are not extracted in an event, that's a passing scenario
            # The count of the field may or may not be same with the count of event. 
            sourcetype_fields = dict()
            for each_result in results:
                sourcetype_fields.setdefault(each_result["sourcetype"], list()).extend(
                    [each_result["field_count"], each_result["valid_field_count"]] 
                )
            for sourcetype_fields in sourcetype_fields.values():
                assert len(set(sourcetype_fields)) == 1, (
                    "All fields from the field-cluster should be extracted with valid values if any one field is extracted."
                    f"\n{test_helper.format_exc_message()}"
                )

    @pytest.mark.splunk_searchtime_cim
    @pytest.mark.splunk_searchtime_cim_fields_not_extracted
    def test_cim_not_extracted_fields(
        self, splunk_search_util, splunk_searchtime_cim_fields_not_extracted, record_property
    ):
        # Search Query

        base_search = "search"
        for each_set in splunk_searchtime_cim_fields_not_extracted["data_set"]:
            base_search += " ({})".format(each_set.search_constraints)

        base_search += " AND ({}) ".format(
            splunk_searchtime_cim_fields_not_extracted["tag_stanza"]
        )

        base_search += " AND ("
        for each_field in splunk_searchtime_cim_fields_not_extracted["fields"]:
            base_search += " ({}=*) OR".format(each_field.name)

        # To remove the extra OR at the end of search
        base_search = base_search[:-2]
        base_search += ")"

        if not splunk_searchtime_cim_fields_not_extracted["tag_stanza"]:
            base_search = base_search.replace("search OR", "search")

        base_search += " | stats "

        for each_field in splunk_searchtime_cim_fields_not_extracted["fields"]:
            base_search += " count({fname}) AS {fname}".format(fname=each_field.name)

        base_search += " by sourcetype"
        record_property("search", base_search)

        results = list(
            splunk_search_util.getFieldValuesList(
                base_search, interval=INTERVAL, retries=RETRIES
            )
        )

        violations = []
        if results:
            violations = [
                [each_elem["sourcetype"], field.name, each_elem.get(field.name)]
                for each_elem in results
                for field in splunk_searchtime_cim_fields_not_extracted["fields"]
                if not each_elem.get(field.name) == "0"
                and not each_elem.get(field.name) == each_elem["sourcetype"]
            ]

            violation_str = (
                "\n These fields are automatically provided by asset and identity"
                " correlation features of applications like Splunk Enterprise Security."
                "\n Do not define extractions for these fields when writing add-ons.\n"
                " Expected eventcount: 0 \n"
            )
            violation_str += FieldTestHelper.get_table_output(
                headers=["Sourcetype", "Fields", "Event Count"], value_list=violations
            )

        assert not violations, violation_str

    @pytest.mark.splunk_searchtime_cim
    @pytest.mark.splunk_searchtime_cim_fields_not_allowed
    def test_cim_not_allowed_fields(
        self, splunk_searchtime_cim_fields_not_allowed, record_property
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
                for data in splunk_searchtime_cim_fields_not_allowed["fields"]
            ],
        )

        assert not splunk_searchtime_cim_fields_not_allowed["fields"], result_str
       
    @pytest.mark.parametrize(
        "app_name", [pytest.param("Splunk_SA_CIM", marks=[pytest.mark.splunk_searchtime_cim])]
    )
    def test_app_installed(self, splunk_search_util, app_name, record_property):
        """
        This test case checks that addon is installed/enabled in the Splunk instance.

        Args:
            splunk_search_util (SearchUtil): Object that helps to search on Splunk.
            app_name (string): Add-on name.
            record_property (fixture): Document facts of test cases.
        """

        record_property("app_name", app_name)
        # Search Query
        search = "| rest /servicesNS/nobody/{}/configs/conf-app/ui".format(app_name)
        self.logger.info(f"Executing the search query: {search}")
        record_property("search", search)

        result = splunk_search_util.checkQueryCountIsGreaterThanZero(
            search, interval=INTERVAL, retries=RETRIES
        )

        assert result, (
            f"\nMessage: App {app_name} is not installed/enabled in this Splunk instance."
            f"The plugin requires the {app_name} to be installed/enabled in the Splunk instance."
            f"Please install the app and execute the tests again."
        )
