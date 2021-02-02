import pytest
from unittest.mock import Mock


@pytest.fixture()
def parser(request):
    class FakeConfigurationFile:
        def __init__(self, sects):
            self.headers = []
            self.sects = sects
            self.errors = []

    FakeApp = Mock()
    attrs = {
        "{}.return_value".format(request.param["func_name"]): FakeConfigurationFile(
            request.param["parsed_output"]
        )
    }
    FakeApp.configure_mock(**attrs)

    return request.param["tested_class"]("fake_path", FakeApp)


"""
class FakeConfigurationSection:
    def __init__(self, options):
        self.options = options


class FakeConfigurationSetting:
    def __init__(self, name, value):
        self.name = name
        self.value = value


parsed_output = {
                "eventtype=fiction_for_tags_positive": FakeConfigurationSection(
                    {'tags_positive_event': FakeConfigurationSetting('tags_positive_event', 'enabled'),
                     'tags_disabled_event': FakeConfigurationSetting('tags_disabled_event', 'disabled')}
                ),
                "source=%2Fopt%2Fsplunk%2Fvar%2Flog%2Fsplunk%2Fsplunkd.log": FakeConfigurationSection(
                    {'tags_positive_event': FakeConfigurationSetting('tags_positive_event', 'enabled'),
                     'tags_disabled_event': FakeConfigurationSetting('tags_disabled_event', 'disabled')}
                )
            }
"""


@pytest.fixture()
def build_parsed_output(request):
    """
    builds expected parser output from provided
    :param request: dictionary with {stanza: {option: value, ...}, ...}
    :return: parsed_output:
    """
    components = request.param
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
