import pytest
from unittest.mock import patch, PropertyMock
from pytest_splunk_addon.standard_lib.addon_parser.tags_parser import (
    TagsParser,
)


output_to_build = {
    "eventtype=fiction_for_tags_positive": {
        "tags_positive_event": "enabled",
        "tags_disabled_event": "disabled",
    },
    "source=%2Fopt%2Fsplunk%2Fvar%2Flog%2Fsplunk%2Fsplunkd.log": {
        "tags_positive_event": "enabled",
        "tags_disabled_event": "disabled",
    },
}


def test_tags_can_be_parsed_and_extracted(parser_instance):
    assert list(parser_instance.tags.sects.keys()) == [
        "eventtype=fiction_for_tags_positive",
        "source=%2Fopt%2Fsplunk%2Fvar%2Flog%2Fsplunk%2Fsplunkd.log",
    ], "tags can not be called or does not have sects attribute"


def test_tags_can_be_parsed_and_returned(parser_instance):
    expected_outputs = [
        {
            "stanza": 'eventtype="fiction_for_tags_positive"',
            "tag": "tags_positive_event",
            "enabled": True,
        },
        {
            "stanza": 'eventtype="fiction_for_tags_positive"',
            "tag": "tags_disabled_event",
            "enabled": False,
        },
        {
            "stanza": 'source="/opt/splunk/var/log/splunk/splunkd.log"',
            "tag": "tags_positive_event",
            "enabled": True,
        },
        {
            "stanza": 'source="/opt/splunk/var/log/splunk/splunkd.log"',
            "tag": "tags_disabled_event",
            "enabled": False,
        },
    ]
    for i, event in enumerate(parser_instance.get_tags()):
        assert event == expected_outputs[i], "expeceted event {} not found".format(
            expected_outputs[i]
        )


def test_get_tags_calls_app_get_config(parser_instance):
    for _ in parser_instance.get_tags():
        pass
    parser_instance.app.get_config.assert_called_once()


def test_no_tags_config_file(parser_instance):
    parser_instance.app.get_config.side_effect = OSError
    assert parser_instance.tags is None, "tags created when no config file exists"


def test_nothing_returned_when_no_tags_config_file(parser):
    with patch.object(TagsParser, "tags", new_callable=PropertyMock) as tags_mock:
        tags_mock.return_value = None
        parser_instance = parser(TagsParser, "get_config", {})
        output = [tag for tag in parser_instance.get_tags() if tag]
        assert output == [], "tags returned when no config file exists"


@pytest.fixture(scope="module")
def parsed_output(build_parsed_output):
    return build_parsed_output(output_to_build)


@pytest.fixture()
def parser_instance(parsed_output, parser):
    return parser(TagsParser, "get_config", parsed_output)
