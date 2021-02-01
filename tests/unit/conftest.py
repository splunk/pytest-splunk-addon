import pytest
from unittest.mock import Mock


@pytest.fixture()
def parser(request):
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
    attrs = {
        "{}.return_value".format(request.param["func_name"]): FakeConfigurationFile()
    }
    FakeApp.configure_mock(**attrs)

    return request.param["tested_class"]("fake_path", FakeApp)
