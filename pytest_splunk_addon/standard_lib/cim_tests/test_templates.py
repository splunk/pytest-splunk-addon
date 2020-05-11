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

    @pytest.mark.parametrize(
        "app_name",
        [pytest.param("Splunk_SA_CIM", marks=[pytest.mark.splunk_searchtime_cim])],
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
            f"App {app_name} is not installed/enabled in this Splunk instance."
            f"\nThe plugin requires the {app_name} to be installed/enabled in the Splunk instance."
            f"\nPlease install the app and execute the tests again."
        )

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

        cim_data_set = splunk_searchtime_cim_fields["data_set"]
        cim_fields = splunk_searchtime_cim_fields["fields"]
        cim_tag_stanza = splunk_searchtime_cim_fields["tag_stanza"]
        # Search Query
        base_search = ""
        for each_set in cim_data_set:
            base_search += " | search {}".format(each_set.search_constraints)

        base_search += " | search {}".format(cim_tag_stanza)

        test_helper = FieldTestHelper(
            splunk_search_util, cim_fields, interval=INTERVAL, retries=RETRIES
        )
        # Execute the query and get the results
        results = test_helper.test_field(base_search)
        record_property("search", test_helper.search)

        # All assertion are made in the same tests to make the test report with
        # very clear order of scenarios. with this approach, a user will be able to identify
        # what went wrong very quickly.

        if len(cim_fields) == 0:
            # If no fields are there, check that the events are mapped
            # with the data model
            assert results, (
                "0 Events mapped with the dataset."
                f"\n{test_helper.format_exc_message()}"
            )
        if len(cim_fields) == 1:
            test_field = cim_fields[0]
            # If the field is required,
            #   there should be events mapped with the data model
            # If the field is conditional,
            #   It's fine if no events matched the condition
            if not test_field.type == "conditional":
                assert results, (
                    "0 Events mapped with the dataset."
                    f"\n{test_helper.format_exc_message()}"
                )
            # The field should be extracted if event count > 0
            for each_field in results:
                assert not each_field["field_count"] == 0, (
                        f"Field {test_field} is not extracted in any events."
                        f"\n{test_helper.format_exc_message()}"
                )
                if each_field["field_count"] > each_field["event_count"]:
                    raise AssertionError(
                        f"Field {test_field} should not be multi-value."
                        f"\n{test_helper.format_exc_message()}"
                    )
                elif each_field["field_count"] < each_field["event_count"]:
                    # The field should be extracted in all events mapped
                    raise AssertionError(
                        f"Field {test_field} is not extracted in some events."
                        f"\n{test_helper.format_exc_message()}"
                    )
                assert each_field["field_count"] == each_field["valid_field_count"], (
                    f"Field {test_field} has invalid values."
                    f"\n{test_helper.format_exc_message()}"
                )
        elif len(cim_fields) > 1:
            # Check that count for all the fields in cluster is same.
            # If all the fields are not extracted in an event, that's a passing scenario
            # The count of the field may or may not be same with the count of event.
            sourcetype_fields = dict()
            for each_result in results:
                sourcetype_fields.setdefault(
                    (each_result["source"], each_result["sourcetype"]), list()
                ).extend([each_result["field_count"], each_result["valid_field_count"]])
            for sourcetype_fields in sourcetype_fields.values():
                assert len(set(sourcetype_fields)) == 1, (
                    "All fields from the field-cluster should be extracted with valid values if any one field is extracted."
                    f"\n{test_helper.format_exc_message()}"
                )

    @pytest.mark.splunk_searchtime_cim
    @pytest.mark.splunk_searchtime_cim_fields_not_allowed_in_search
    def test_cim_fields_not_allowed_in_search(
        self,
        splunk_search_util,
        splunk_searchtime_cim_fields_not_allowed_in_search,
        record_property,
    ):
        cim_dataset = splunk_searchtime_cim_fields_not_allowed_in_search["data_set"]
        cim_fields = splunk_searchtime_cim_fields_not_allowed_in_search["fields"]
        cim_tag_stanza = splunk_searchtime_cim_fields_not_allowed_in_search[
            "tag_stanza"
        ]

        # Search Query

        base_search = "search"
        for each_set in cim_dataset:
            base_search += " | search {}".format(each_set.search_constraints)

        base_search += " | search {}".format(cim_tag_stanza)

        base_search += " AND ("
        for each_field in cim_fields:
            base_search += " ({}=*) OR".format(each_field.name)

        # To remove the extra OR at the end of search
        base_search = base_search[:-2]
        base_search += ")"

        if not cim_tag_stanza:
            base_search = base_search.replace("search OR", "search")

        base_search += " | stats "

        for each_field in cim_fields:
            base_search += " count({fname}) AS {fname}".format(fname=each_field.name)

        base_search += " by source, sourcetype"
        record_property("search", base_search)
        self.logger.info("base_search: %s", base_search)
        results = list(
            splunk_search_util.getFieldValuesList(
                base_search, interval=INTERVAL, retries=RETRIES
            )
        )

        violations = []
        if results:
            violations = [
                [
                    each_elem["source"],
                    each_elem["sourcetype"],
                    field.name,
                    each_elem.get(field.name),
                ]
                for each_elem in results
                for field in cim_fields
                if not each_elem.get(field.name) == "0"
                and not each_elem.get(field.name) == each_elem["sourcetype"]
            ]

            violation_str = (
                "The fields should not be extracted in the dataset"
                "\nThese fields are automatically provided by asset and identity"
                " correlation features of applications like Splunk Enterprise Security."
                "\nDo not define extractions for these fields when writing add-ons."
                "\nExpected eventcount: 0 \n\n"
            )
            violation_str += FieldTestHelper.get_table_output(
                headers=["Source", "Sourcetype", "Fields", "Event Count"],
                value_list=violations,
            )

        assert not violations, violation_str

    @pytest.mark.splunk_searchtime_cim
    @pytest.mark.splunk_searchtime_cim_fields_not_allowed_in_props
    def test_cim_fields_not_allowed_in_props(
        self, splunk_searchtime_cim_fields_not_allowed_in_props, record_property
    ):
        result_str = (
            "The field extractions are not allowed in the configuration files"
            "\nThese fields are automatically provided by asset and identity"
            " correlation features of applications like Splunk Enterprise Security."
            "\nDo not define extractions for these fields when writing add-ons.\n\n"
        )

        result_str += FieldTestHelper.get_table_output(
            headers=["Stanza", "Classname", "Fieldname"],
            value_list=[
                [data["stanza"], data["classname"], data["name"]]
                for data in splunk_searchtime_cim_fields_not_allowed_in_props["fields"]
            ],
        )

        assert not splunk_searchtime_cim_fields_not_allowed_in_props[
            "fields"
        ], result_str

    @pytest.mark.splunk_searchtime_cim
    @pytest.mark.splunk_searchtime_cim_mapped_datamodel
    def test_eventtype_mapped_multiple_cim_datamodel(
        self, splunk_search_util, record_property, caplog
    ):
        """
        This test case check that event type is not be mapped with more than one data model 

        Args:
            splunk_search_util (SearchUtil): Object that helps to search on Splunk.
            record_property (fixture): Document facts of test cases.
            caplog (fixture): fixture to capture logs.
        """

        data_models = [
            "Alerts",
            "Authentication",
            "Certificates",
            "Change",
            "Compute_Inventory",
            "DLP",
            "Databases",
            "Email",
            "Endpoint",
            "Event_Signatures",
            "Interprocess_Messaging",
            "Intrusion_Detection",
            "JVM",
            "Malware",
            "Network_Resolution",
            "Network_Sessions",
            "Network_Traffic",
            "Performance",
            "Splunk_Audit",
            "Ticket_Management",
            "Updates",
            "Vulnerabilities",
            "Web",
        ]

        search = ""
        # Iterate data models list to create a search query
        for index, datamodel in enumerate(data_models):
            if index == 0:
                search += f'| tstats count from datamodel={datamodel}  by eventtype | eval dm_type="{datamodel}"\n'
            elif datamodel == "Splunk_Audit":
                # Exclude the internal search logs in the results
                search += f'| append [| tstats count from datamodel={datamodel} WHERE index!="_*"  by eventtype | eval dm_type="{datamodel}"]\n'
            else:
                search += f'| append [| tstats count from datamodel={datamodel}  by eventtype | eval dm_type="{datamodel}"]\n'

        search += """| stats delim=", " dc(dm_type) as datamodel_count, values(dm_type) as datamodels by eventtype | nomv datamodels
        | where datamodel_count > 1 and eventtype!="err0r"
        """
        record_property("search", search)

        results = list(splunk_search_util.getFieldValuesList(search, INTERVAL, RETRIES))
        if results:
            record_property("results", results)
            result_str = FieldTestHelper.get_table_output(
                headers=["Count", "Eventtype", "Datamodels"],
                value_list=[
                    [
                        each_result["datamodel_count"],
                        each_result["eventtype"],
                        each_result["datamodels"],
                    ]
                    for each_result in results
                ],
            )

        assert not results, (
            "Multiple data models are mapped with an eventtype"
            f"\nQuery result greater than 0.\nsearch=\n{search} \n \n"
            f"Event type which associated with multiple data model \n{result_str}"
        )
