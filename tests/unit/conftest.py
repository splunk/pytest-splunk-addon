import pytest
from collections import namedtuple


@pytest.fixture
def fake_app(mocker):
    def func(cf):
        fa = mocker.Mock()
        fa.eventtypes = cf
        fa.eventtypes_conf.return_value = cf
        fa.props_conf.return_value = cf
        return fa

    return func


@pytest.fixture
def configuration_file():
    def func(headers, sects, errors):
        ConfigurationFile = namedtuple(
            "ConfigurationFile", ["headers", "sects", "errors"]
        )
        return ConfigurationFile(headers, sects, errors)

    return func


@pytest.fixture(scope="session")
def parser():
    def create_parser(parser_class, func_to_be_mocked, parsed_output):
        class FakeConfigurationFile:
            def __init__(self, sects):
                self.headers = []
                self.sects = sects
                self.errors = []

        FakeApp = Mock()
        attrs = {
            "{}.return_value".format(func_to_be_mocked): FakeConfigurationFile(
                parsed_output
            )
        }
        FakeApp.configure_mock(**attrs)
        return parser_class("fake_path", FakeApp)

    return create_parser


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
