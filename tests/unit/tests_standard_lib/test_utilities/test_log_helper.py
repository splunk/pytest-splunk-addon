import pytest
from unittest.mock import patch, MagicMock
from pytest_splunk_addon.standard_lib.utilities.log_helper import get_table_output
from pytest_splunk_addon.standard_lib.utilities.log_helper import (
    format_search_query_log,
)


@pytest.mark.parametrize(
    "headers, value_list, expected_output",
    [
        (
            ["Header1", "Header2"],
            [["One", "Value1"], ["Two", "Value2"]],
            "Header1 | Header2\n------- | -------\nOne     | Value1 \nTwo     | Value2 \n",
        ),
        (
            ["header", "long header"],
            [["field", "val1"], ["long field", "val2"]],
            "header     | long header\n---------- | -----------\nfield      | val1       \nlong field | val2       \n",
        ),
    ],
)
def test_get_table_output(headers, value_list, expected_output):
    assert get_table_output(headers, value_list) == expected_output


@pytest.mark.parametrize(
    "search_query, expected_output",
    [
        (
            'search (index=*) AND eventtype="sophos_sec_web" | stats count by sourcetype',
            '\nSearch query:\nsearch (index=*) AND eventtype="sophos_sec_web" \n| stats count by sourcetype\n\nSearch query to copy:\nsearch (index=*) AND eventtype="sophos_sec_web" | stats count by sourcetype\n',
        )
    ],
)
def test_format_search_query_log(search_query, expected_output):
    assert format_search_query_log(search_query) == expected_output
