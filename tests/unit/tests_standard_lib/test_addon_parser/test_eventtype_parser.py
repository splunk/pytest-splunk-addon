from unittest.mock import PropertyMock, patch

import pytest

from pytest_splunk_addon.standard_lib.addon_parser.eventtype_parser import (
    EventTypeParser,
)

output_to_build = {
    "fiction_is_splunkd": {"search": "index=_internal sourcetype=splunkd"},
    "fiction_for_tags_positive": {"search": "sourcetype=splunkd"},
    "fiction_is_splunkd-%host%": {"search": "index=_internal sourcetype=splunkd"},
}


def test_eventtypes_can_be_parsed_and_extracted(parser_instance):
    assert list(parser_instance.eventtypes.sects.keys()) == [
        "fiction_is_splunkd",
        "fiction_for_tags_positive",
        "fiction_is_splunkd-%host%",
    ], "eventypes can not be called or does not have sects attribute"


def test_eventtypes_can_be_parsed_and_returned(parsed_output, parser_instance):
    expected_outputs = [{"stanza": x} for x in parsed_output.keys()]
    for i, event in enumerate(parser_instance.get_eventtypes()):
        assert event == expected_outputs[i], "expeceted event {} not found".format(
            expected_outputs[i]
        )


def test_get_eventtypes_calls_app_get_config(parser_instance):
    for _ in parser_instance.get_eventtypes():
        pass
    parser_instance.app.eventtypes_conf.assert_called_once()


def test_no_eventtype_config_file(parser_instance):
    parser_instance.app.eventtypes_conf.side_effect = OSError
    assert (
        parser_instance.eventtypes is None
    ), "eventtypes created when no config file exists"


def test_nothing_returned_when_no_tags_config_file(parser):
    with patch.object(
        EventTypeParser, "eventtypes", new_callable=PropertyMock
    ) as eventtypes_mock:
        eventtypes_mock.return_value = None
        parser_instance = parser(EventTypeParser, "eventtypes_conf", {})
        output = [tag for tag in parser_instance.get_eventtypes() if tag]
        assert output == [], "eventtypes returned when no config file exists"


@pytest.fixture(scope="module")
def parsed_output(build_parsed_output):
    return build_parsed_output(output_to_build)


@pytest.fixture()
def parser_instance(parsed_output, parser):
    return parser(EventTypeParser, "eventtypes_conf", parsed_output)
