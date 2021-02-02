import pytest
from pytest_splunk_addon.standard_lib.addon_parser.eventtype_parser import (
    EventTypeParser,
)


output_to_build = {
    "fiction_is_splunkd": {"search": "index=_internal sourcetype=splunkd"},
    "fiction_for_tags_positive": {
        "search": "sourcetype=splunkd",
    },
    "fiction_is_splunkd-%host%": {
        "search": "index=_internal sourcetype=splunkd",
    },
}


def test_eventtypes_can_be_parsed_and_extracted(parser_instance):
    assert hasattr(
        parser_instance.eventtypes, "sects"
    ), "eventypes can not be called or does have sects attribute"


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
    output = [eventtype for eventtype in parser_instance.get_eventtypes() if eventtype]
    assert output == [], "eventtypes created when no config file exists"


@pytest.fixture()
def parsed_output(build_parsed_output):
    return build_parsed_output(output_to_build)


@pytest.fixture()
def parser_instance(parsed_output, parser):
    return parser(EventTypeParser, "eventtypes_conf", parsed_output)
