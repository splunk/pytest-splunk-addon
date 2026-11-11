#
# Copyright 2024 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# -*- coding: utf-8 -*-
"""
Base class for test cases. Provides test cases to verify
field extractions and CIM compatibility.
"""

from ..fields_tests import FieldTestTemplates
from ..cim_tests import CIMTestTemplates
from ..index_tests import IndexTimeTestTemplate
from ..utilities.log_helper import get_table_output
import json
import re
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
        self, request, splunk_search_util, splunk_ingest_data, splunk_setup, record_property
    ):
        """
        Test case to validate that all the events have been properly tokenised

        Args:
            splunk_search_util (SearchUtil): Object that helps to search on Splunk.
            splunk_ingest_data (fixture): To ingest data into splunk.
            record_property (fixture): Document facts of test cases.

        """
        sourcetype_patterns = json.loads(
            request.config.getoption("untokenised_sourcetype_patterns")
        )
        if sourcetype_patterns:
            if not isinstance(sourcetype_patterns, list) or not all(
                isinstance(pattern, str)
                and re.fullmatch(r"[A-Za-z0-9_.:-]+\*?", pattern)
                for pattern in sourcetype_patterns
            ):
                raise ValueError("Invalid --untokenised-sourcetype-patterns value")
            sourcetype_filter = " OR ".join(
                f'sourcetype="{pattern}"' for pattern in sourcetype_patterns
            )
            query = (
                f'''search index=* ({sourcetype_filter}) '''
                f'''| regex _raw="##[a-zA-Z0-9_-]+##" '''
                f'''| stats count by source, sourcetype'''
            )
        else:
            query = (
                'search index=* | regex _raw="##[a-zA-Z0-9_-]+##" '
                '| stats count by source, sourcetype'
            )
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
            result_str = get_table_output(
                headers=["Source", "Sourcetype"],
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
