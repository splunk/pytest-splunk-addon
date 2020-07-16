# -*- coding: utf-8 -*-
"""
Base class for test cases. Provides test cases to verify
field extractions and CIM compatibility.
"""

from .fields_tests import FieldTestTemplates
from .cim_tests import CIMTestTemplates, FieldTestHelper
from .index_tests import IndexTimeTestTemplate
import pytest

class Basic(FieldTestTemplates, CIMTestTemplates, IndexTimeTestTemplate):
    """
    Base class for test cases. Inherit this class to include the test 
    cases for an Add-on. Only implement the common tests here, all the other 
    specific test case should be implemented in a TestTemplate class and Basic 
    should inherit it.
    """
    
    @pytest.mark.first
    @pytest.mark.splunk_indextime
    @pytest.mark.splunk_searchtime_cim
    @pytest.mark.splunk_searchtime_fields
    def test_events_with_untokenised_values(
        self,
        splunk_search_util,
        splunk_ingest_data,
        record_property
    ):
        """
        Test case to validate that all the events have been properly tokenised

        Args:
            splunk_search_util (SearchUtil): Object that helps to search on Splunk.
            splunk_ingest_data (fixture): To ingest data into splunk.
            record_property (fixture): Document facts of test cases.

        """
        query =f'search index=* ##*## | stats count by source, sourcetype'
        record_property("Query", query)
        results = list(
            splunk_search_util.getFieldValuesList(
                query,
                interval=0,
                retries=0,
            )
        )
        if results:
            record_property("results", results)
            result_str = FieldTestHelper.get_table_output(
                headers=["Source","Sourcetype"],
                value_list=[
                    [
                        result.get("source"),
                        result.get("sourcetype"),
                    ]
                    for result in results
                ],
            )
            assert False, (
                f"For the query: '{query}'\n"
                f"Some fields are not tokenized in the events of following source and sourcetype \n{result_str}"
            )
