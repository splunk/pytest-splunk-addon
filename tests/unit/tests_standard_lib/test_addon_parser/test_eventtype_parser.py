from unittest.mock import mock_open, patch

from pytest_splunk_addon.standard_lib.addon_parser.eventtype_parser import (
    EventTypeParser,
)

TEST_EVENTTYPES = """[fiction_is_splunkd]
search = index=_internal sourcetype=splunkd

[fiction_for_tags_positive]
search = sourcetype=splunkd

[fiction_is_splunkd-%host%]
search = index=_internal sourcetype=splunkd
"""


def test_eventtypes_can_be_parsed_and_returned():
    expected_outputs = [
        {"stanza": "fiction_is_splunkd"},
        {"stanza": "fiction_for_tags_positive"},
        {"stanza": "fiction_is_splunkd-%host%"},
    ]
    eventtypes_parser = EventTypeParser("unused_path")
    with patch("builtins.open", new_callable=mock_open, read_data=TEST_EVENTTYPES):
        output = eventtypes_parser.get_eventtypes()
        assert expected_outputs == list(output)


def test_no_eventtypes_config_file():
    eventtypes_parser = EventTypeParser("unused_path")
    with patch("builtins.open", mock_open()) as mock_file:
        mock_file.side_effect = OSError()
        assert eventtypes_parser.eventtypes is None
