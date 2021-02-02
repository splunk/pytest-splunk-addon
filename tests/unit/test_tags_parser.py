import pytest
from pytest_splunk_addon.standard_lib.addon_parser.tags_parser import (
    TagsParser,
    unquote,
)
from unittest.mock import Mock


class FakeConfigurationSection:
    def __init__(self, options):
        self.options = options


class FakeConfigurationSetting:
    def __init__(self, name, value):
        self.name = name
        self.value = value


def build_parsed_output(components):
    """
    builds expected parser output from provided
    :param request: dictionary with {stanza: {option: value, ...}, ...}
    :return: parsed_output:
    """
    parsed_output = {}
    for stanza, stanza_value in components.items():
        fake_section = Mock()
        fake_section.options = {}
        parsed_output.update({stanza: fake_section})
        for option, value in stanza_value.items():
            fake_setting = Mock()
            fake_setting.name = option
            fake_setting.value = value
            parsed_output[stanza].options.update({option: fake_setting})
    return parsed_output


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
parsed_output = build_parsed_output(output_to_build)

pytest_args = [
    "parser",
    [
        {
            "tested_class": TagsParser,
            "func_name": "get_config",
            "parsed_output": parsed_output,
        }
    ],
]


@pytest.mark.parametrize(
    *pytest_args,
    indirect=True,
)
def test_tags_can_be_parsed_and_extracted(parser):
    assert hasattr(
        parser.tags, "sects"
    ), "tags can not be called or does have sects attribute"


@pytest.mark.parametrize(
    *pytest_args,
    indirect=True,
)
def test_tags_can_be_parsed_and_returned(parser):
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
    for i, event in enumerate(parser.get_tags()):
        assert event == expected_outputs[i], "expeceted event {} not found".format(
            expected_outputs[i]
        )


@pytest.mark.parametrize(
    *pytest_args,
    indirect=True,
)
def test_get_tags_calls_app_get_config(parser):
    for _ in parser.get_tags():
        pass
    parser.app.get_config.assert_called_once()


@pytest.mark.parametrize(
    *pytest_args,
    indirect=True,
)
def test_no_tags_config_file(parser):
    parser.app.get_config.side_effect = OSError
    output = [tag for tag in parser.get_tags() if tag]
    assert output == [], "tags created when no config file exists"
