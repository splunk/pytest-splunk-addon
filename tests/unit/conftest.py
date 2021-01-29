import pytest
from unittest.mock import Mock
from pytest_splunk_addon.standard_lib.addon_parser.eventtype_parser import (
    EventTypeParser,
)


@pytest.fixture()
def parser():
    class FakeConfigurationFile:
        def __init__(self):
            self.headers = []
            self.sects = {
                "fake_splunkd": {
                    "name": "fake_splunkd",
                    "options": "index=_internal sourcetype=splunkd",
                },
                "fake_for_tags_positive": {
                    "name": "fake_for_tags_positive",
                    "options": "sourcetype=splunkd",
                },
            }
            self.errors = []

    FakeApp = Mock()
    FakeApp.eventtypes = FakeConfigurationFile()
    FakeApp.eventtypes_conf.return_value = FakeConfigurationFile()

    return EventTypeParser("fake_path", FakeApp)
