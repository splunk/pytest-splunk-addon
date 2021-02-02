import pytest
from pytest_splunk_addon.standard_lib.addon_parser.tags_parser import (
    TagsParser,
    unquote,
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
    assert hasattr(
        parser_instance.tags, "sects"
    ), "tags can not be called or does have sects attribute"


def test_tags_can_be_parsed_and_returned(parsed_output, parser_instance):
    expected_outputs = []
    for stanza, section in parsed_output.items():
        stanza = stanza.replace("=", '="')
        stanza = unquote('{}"'.format(stanza))
        for item, value in section.options.items():
            expected_outputs.append(
                {
                    "stanza": stanza,
                    "tag": value.name,
                    "enabled": True if value.value == "enabled" else False,
                }
            )
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
    output = [tag for tag in parser_instance.get_tags() if tag]
    assert output == [], "tags created when no config file exists"


@pytest.fixture()
def parsed_output(build_parsed_output):
    return build_parsed_output(output_to_build)


@pytest.fixture()
def parser_instance(parsed_output, parser):
    return parser(TagsParser, "get_config", parsed_output)
