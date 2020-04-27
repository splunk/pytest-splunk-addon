# -*- coding: utf-8 -*-
"""
Includes the test scenarios to check the CIM compatibility of an Add-on.
"""

import logging
import pytest

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
