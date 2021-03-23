import pytest
from unittest.mock import MagicMock, mock_open
from collections import namedtuple


@pytest.fixture()
def open_mock(monkeypatch):
    open_mock = mock_open()
    monkeypatch.setattr("builtins.open", open_mock)
    return open_mock


@pytest.fixture()
def json_load_mock(monkeypatch):
    load_mock = MagicMock()
    monkeypatch.setattr("json.load", load_mock)
    return load_mock


@pytest.fixture()
def argparse_mock(monkeypatch):
    ap = MagicMock()
    ap.return_value = ap
    monkeypatch.setattr("argparse.ArgumentParser", ap)
    return ap


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
            fake_section = MagicMock()
            fake_section.options = {}
            fake_section.name = stanza
            parsed_output.update({stanza: fake_section})
            for option, value in stanza_value.items():
                fake_setting = MagicMock()
                fake_setting.name = option
                fake_setting.value = value
                parsed_output[stanza].options.update({option: fake_setting})
        return parsed_output

    return parsed_output
