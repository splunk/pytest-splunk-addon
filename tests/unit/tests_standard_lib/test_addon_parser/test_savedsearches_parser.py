import pytest
from unittest.mock import patch, PropertyMock
from pytest_splunk_addon.standard_lib.addon_parser.savedsearches_parser import (
    SavedSearchParser,
)

output_to_build = {
    "basic_search": {
        "search": "_internal | stats count by sourcetype",
    },
    "search_earliest_time": {
        "search": "index = _internal | stats count by sourcetype | outputlookup saved_search_data.csv",
        "dispatch.earliest_time": "-4d",
    },
    "empty_search_latest_time": {
        "search": "",
        "dispatch.latest_time": "-1s",
    },
}


@pytest.fixture(scope="module")
def parsed_output(build_parsed_output):
    return build_parsed_output(output_to_build)


@pytest.fixture()
def parser_instance(parsed_output, parser):
    return parser(SavedSearchParser, "get_config", parsed_output)


def test_savedsearches(parser_instance):
    assert list(parser_instance.savedsearches.sects.keys()) == [
        "basic_search",
        "search_earliest_time",
        "empty_search_latest_time",
    ]
    parser_instance.app.get_config.assert_called_once_with("savedsearches.conf")


def test_no_savedsearches_config_file(parser_instance):
    parser_instance.app.get_config.side_effect = OSError
    assert parser_instance.savedsearches is None


def test_get_savedsearches(parser_instance):
    out = list(parser_instance.get_savedsearches())
    assert out == [
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


def test_get_savedsearches_without_config_file(parser):
    with patch.object(
        SavedSearchParser, "savedsearches", new_callable=PropertyMock
    ) as savedsearches_mock:
        savedsearches_mock.return_value = None
        parser_instance = parser(SavedSearchParser, "get_config", {})
        output = [search for search in parser_instance.get_savedsearches() if search]
        assert output == [], "savedsearches returned when no config file exists"
