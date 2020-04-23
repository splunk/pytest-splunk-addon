# -*- coding: utf-8 -*-
"""
Includes the test scenarios to check the CIM compatibility of an Add-on.
"""
import logging
import pytest

DATA_MODELS = [
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

    def test_eventtype_mapped_datamodel(
        self, splunk_search_util, record_property, caplog
    ):
        """
        This test case check that event type is not be mapped with more than one data model 

        Args:
            splunk_search_util (SearchUtil): Object that helps to search on Splunk.
            record_property (fixture): Document facts of test cases.
            caplog (fixture): fixture to capture logs.
        """

        search = ""
        # Iterate data models list to create a search query
        for index, datamodel in enumerate(DATA_MODELS):
            if index == 0:
                search += f'| tstats count from datamodel={datamodel}  by eventtype | eval dm_type="{datamodel}"\n'
            else:
                search += f'| append [| tstats count from datamodel={datamodel}  by eventtype | eval dm_type="{datamodel}"]\n'

        search += """| stats delim=", " dc(dm_type) as datamodel_count, values(dm_type) as datamodels by eventtype | nomv datamodels
        | where datamodel_count > 1 and eventtype!="err0r"
        """

        record_property("search", search)
        result, results = splunk_search_util.checkQueryCountIsZero(search)
        if not result:
            record_property("results", results.as_list)
            # Iterate results lists to create a table format string
            result_str = "{:<70} {:<20} {:<200} \n".format(
                "Eventtype", "Count", "Datamodels"
            )
            for data in results.as_list:
                result_str += "{:<70} {:<20} {:<200} \n".format(
                    data["eventtype"], data["datamodel_count"], data["datamodels"]
                )

        assert result, (
            f"Query result greater than 0.\nsearch=\n{search} \n \n"
            f"Event type which associated with multiple data model \n{result_str}"
        )
