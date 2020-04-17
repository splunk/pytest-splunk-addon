# -*- coding: utf-8 -*-
"""
Includes the test scenarios to check the CIM compatibility of an Add-on.
"""
import logging
import pytest


class CIMTests:
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
        search = """
            | tstats count from datamodel=Alerts  by eventtype | eval dm_type="Alerts" 
            | append [| tstats count from datamodel=Application_State  by eventtype | eval dm_type="Application_State"] 
            | append [| tstats count from datamodel=Authentication  by eventtype | eval dm_type="Authentication"] 
            | append [| tstats count from datamodel=Certificates  by eventtype | eval dm_type="Certificates"] 
            | append [| tstats count from datamodel=Change  by eventtype | eval dm_type="Change"] 
            | append [| tstats count from datamodel=Change_Analysis  by eventtype | eval dm_type="Change_Analysis"] 
            | append [| tstats count from datamodel=Compute_Inventory  by eventtype | eval dm_type="Compute_Inventory"] 
            | append [| tstats count from datamodel=DLP  by eventtype | eval dm_type="DLP"] 
            | append [| tstats count from datamodel=Databases  by eventtype | eval dm_type="Databases"] 
            | append [| tstats count from datamodel=Email  by eventtype | eval dm_type="Email"] 
            | append [| tstats count from datamodel=Endpoint  by eventtype | eval dm_type="Endpoint"] 
            | append [| tstats count from datamodel=Event_Signatures  by eventtype | eval dm_type="Event_Signatures"] 
            | append [| tstats count from datamodel=Interprocess_Messaging  by eventtype | eval dm_type="Interprocess_Messaging"] 
            | append [| tstats count from datamodel=Intrusion_Detection  by eventtype | eval dm_type="Intrusion_Detection"] 
            | append [| tstats count from datamodel=JVM  by eventtype | eval dm_type="JVM"] 
            | append [| tstats count from datamodel=Malware  by eventtype | eval dm_type="Malware"] 
            | append [| tstats count from datamodel=Network_Resolution  by eventtype | eval dm_type="Network_Resolution"] 
            | append [| tstats count from datamodel=Network_Sessions  by eventtype | eval dm_type="Network_Sessions"] 
            | append [| tstats count from datamodel=Network_Traffic  by eventtype | eval dm_type="Network_Traffic"] 
            | append [| tstats count from datamodel=Performance  by eventtype | eval dm_type="Performance"] 
            | append [| tstats count from datamodel=Splunk_Audit  by eventtype | eval dm_type="Splunk_Audit"] 
            | append [| tstats count from datamodel=Ticket_Management  by eventtype | eval dm_type="Ticket_Management"] 
            | append [| tstats count from datamodel=Updates  by eventtype | eval dm_type="Updates"] 
            | append [| tstats count from datamodel=Vulnerabilities  by eventtype | eval dm_type="Vulnerabilities"] 
            | append [| tstats count from datamodel=Web  by eventtype | eval dm_type="Web"] 
            | stats delim=", " dc(dm_type) as datamodel_count, values(dm_type) as datamodels by eventtype | nomv datamodels | where datamodel_count > 1 and eventtype!="err0r"
        """

        record_property("search", search)
        result, results = splunk_search_util.checkQueryCountIsZero(search)
        if not result:
            record_property("results", results.as_list)
            # Iterate results lists to create a table format string which displays the event type, event type associated data models and count
            result_str = "{:<70} {:<20} {:<200} \n".format(
                "Eventtype", "Count", "Datamodels"
            )
            for data in results.as_list:
                result_str += "{:<70} {:<20} {:<200} \n".format(
                    data["eventtype"], data["datamodel_count"], data["datamodels"]
                )

        assert result, (
            f"Query result greater than 0.\nsearch={search} \n \n"
            f"Event type which associated with multiple data model \n{result_str}"
        )
