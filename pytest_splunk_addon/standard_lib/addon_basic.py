# -*- coding: utf-8 -*-
"""
Base class for test cases. Provides test cases to verify
field extractions and CIM compatibility.
"""

from .fields_tests import FieldTestTemplates
from .cim_tests import CIMTestTemplates

import logging
import pytest

INTERVAL = 3
RETRIES = 3


class Basic(FieldTestTemplates, CIMTestTemplates):
    """
    Base class for test cases. Inherit this class to include the test cases for an Add-on.
    Supported Test scenarios:
        - Check add-ons is installed/enabled in the Splunk instance. 
    """

    logger = logging.getLogger("pytest-splunk-addon-tests")

    @pytest.mark.parametrize(
        "app_name",
        [
            pytest.param("SA-Eventgen", marks=[pytest.mark.field]),
            pytest.param("Splunk_SA_CIM", marks=[pytest.mark.field, pytest.mark.cim]),
        ],
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
