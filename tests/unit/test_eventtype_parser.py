import pytest
from pytest_splunk_addon.standard_lib.addon_parser.eventtype_parser import (
    EventTypeParser,
)


parsed_output = {
    "fake_splunkd": {
        "name": "fake_splunkd",
        "options": "index=_internal sourcetype=splunkd",
    },
    "fake_for_tags_positive": {
        "name": "fake_for_tags_positive",
        "options": "sourcetype=splunkd",
    },
}


pytest_args = [
    "parser",
    [
        {
            "tested_class": EventTypeParser,
            "func_name": "eventtypes_conf",
            "parsed_output": parsed_output,
        }
    ],
]


@pytest.mark.parametrize(
    *pytest_args,
    indirect=True,
)
def test_eventtypes_can_be_parsed_and_extracted(parser):
    assert hasattr(
        parser.eventtypes, "sects"
    ), "eventypes can not be called or does have sects attribute"


@pytest.mark.parametrize(
    *pytest_args,
    indirect=True,
)
def test_eventtypes_can_be_parsed_and_returned(parser):
    expected_outputs = [
        {"stanza": x} for x in ["fake_splunkd", "fake_for_tags_positive"]
    ]
    for i, event in enumerate(parser.get_eventtypes()):
        assert event == expected_outputs[i], "expeceted event {} not found".format(
            expected_outputs[i]
        )


@pytest.mark.parametrize(
    *pytest_args,
    indirect=True,
)
def test_get_eventtypes_calls_app_get_config(parser):
    for _ in parser.get_eventtypes():
        pass
    parser.app.eventtypes_conf.assert_called_once()


@pytest.mark.parametrize(
    *pytest_args,
    indirect=True,
)
def test_no_eventtype_config_file(parser):
    parser.app.eventtypes_conf.side_effect = OSError
    output = [eventtype for eventtype in parser.get_eventtypes() if eventtype]
    assert output == [], "eventtypes created when no config file exists"
