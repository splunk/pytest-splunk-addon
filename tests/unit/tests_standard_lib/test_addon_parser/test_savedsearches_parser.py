from unittest.mock import patch, mock_open
from pytest_splunk_addon.standard_lib.addon_parser.savedsearches_parser import (
    SavedSearchParser,
)

TEST_SAVEDSEARCHES = """[basic_search]
search = _internal | stats count by sourcetype

[search_earliest_time]
search = index = _internal | stats count by sourcetype | outputlookup saved_search_data.csv
dispatch.earliest_time = -4d

[empty_search_latest_time]
search = 
dispatch.latest_time = -1s
"""


def test_get_savedsearches():
    expected_outputs = [
        {
            "stanza": "basic_search",
            "search": "_internal | stats count by sourcetype",
            "dispatch.earliest_time": "0",
            "dispatch.latest_time": "now",
        },
        {
            "stanza": "search_earliest_time",
            "search": "index = _internal | stats count by sourcetype | outputlookup saved_search_data.csv",
            "dispatch.earliest_time": "-4d",
            "dispatch.latest_time": "now",
        },
        {
            "stanza": "empty_search_latest_time",
            "search": 'index = "main"',
            "dispatch.earliest_time": "0",
            "dispatch.latest_time": "-1s",
        },
    ]
    savedsearches_parser = SavedSearchParser("unused_path")
    with patch("builtins.open", new_callable=mock_open, read_data=TEST_SAVEDSEARCHES):
        output = savedsearches_parser.get_savedsearches()
        assert expected_outputs == list(output)


def test_no_savedsearches_config_file():
    savedsearches_parser = SavedSearchParser("unused_path")
    with patch("builtins.open", mock_open()) as mock_file:
        mock_file.side_effect = OSError()
        assert savedsearches_parser.savedsearches is None
