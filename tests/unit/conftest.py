import pytest
from collections import namedtuple
from unittest.mock import Mock


@pytest.fixture
def parser(configuration_file):
    def create_parser(parser_class, func_to_be_mocked, parsed_output, headers=None):
        headers = headers if headers else []
        FakeApp = Mock()
        attrs = {
            "{}.return_value".format(func_to_be_mocked): configuration_file(
                headers=headers, sects=parsed_output, errors=[]
            )
        }
        FakeApp.configure_mock(**attrs)
        return parser_class("fake_path", FakeApp)

    return create_parser


@pytest.fixture
def configuration_file():
    def func(headers, sects, errors):
        ConfigurationFile = namedtuple(
            "ConfigurationFile", ["headers", "sects", "errors"]
        )
        return ConfigurationFile(headers, sects, errors)

    return func


@pytest.fixture(scope="session")
def build_parsed_output():
    def parsed_output(output_elements):
        """
        builds expected parser output from provided dict
        :param output_elements: dictionary with {stanza: {option: value, ...}, ...}
        :return: parsed_output
        """
        parsed_output = {}
        for stanza, stanza_value in output_elements.items():
            fake_section = Mock()
            fake_section.options = {}
            fake_section.name = stanza
            parsed_output.update({stanza: fake_section})
            for option, value in stanza_value.items():
                fake_setting = Mock()
                fake_setting.name = option
                fake_setting.value = value
                parsed_output[stanza].options.update({option: fake_setting})
        return parsed_output

    return parsed_output
