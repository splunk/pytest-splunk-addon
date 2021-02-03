import pytest
from collections import namedtuple
from pytest_splunk_addon.standard_lib.addon_parser.eventtype_parser import (
    EventTypeParser,
)


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


@pytest.fixture
def parser(fake_app, configuration_file):
    return EventTypeParser(
        "fake_path",
        fake_app(
            configuration_file(
                headers=[],
                sects={
                    "fake_splunkd": {
                        "name": "fake_splunkd",
                        "options": "index=_internal sourcetype=splunkd",
                    },
                    "fake_for_tags_positive": {
                        "name": "fake_for_tags_positive",
                        "olptions": "sourcetype=splunkd",
                    },
                },
                errors=[],
            )
        ),
    )
