import pytest
from unittest.mock import patch
from pytest_splunk_addon.standard_lib.addon_parser.eventtype_parser import EventTypeParser


def test_eventtypes_can_be_parsed_and_extracted(parser):
    assert parser.eventtypes, "eventypes can not be called or does not return any value"


def test_eventtypes_can_be_parsed_and_returned(parser):
    expected_outputs = [{"stanza": x} for x in ["fake_splunkd", "fake_for_tags_positive"]]
    for i, event in enumerate(parser.get_eventtypes()):
        assert event == expected_outputs[i], "expeceted event {} not found".format(expected_outputs[i])


def test_get_eventtypes_calls_app_get_config(parser):
    with patch.object(parser.app, "eventtypes_conf") as mock:
        for _ in parser.get_eventtypes():
            pass
        mock.assert_called_once()


def test_no_eventtype_config_file(parser):
    parser.app.eventtypes_conf = os_error
    output = []
    for i in parser.get_eventtypes():
        output.append(i)
    assert not output, "eventtypes created when no config file exists"


@pytest.fixture()
def parser():
    class FakeApp:
        def __init__(self):
            self.splunk_app_path = "fake_path"
            self.eventtypes = FakeConfigurationFile()

        def eventtypes_conf(self):
            return self.eventtypes

    class FakeConfigurationFile:
        def __init__(self):
            self.headers = []
            self.sects = {
                "fake_splunkd": {
                    "name": "fake_splunkd",
                    "options": "index=_internal sourcetype=splunkd"
                },
                "fake_for_tags_positive": {
                    "name": "fake_for_tags_positive",
                    "options": "sourcetype=splunkd"
                }
            }
            self.errors = []

    return EventTypeParser("fake_path", FakeApp())


def os_error():
    raise OSError
