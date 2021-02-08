import importlib
import pytest
from unittest.mock import patch
import sys

with patch.object(
    sys.modules["pytest_splunk_addon.standard_lib.addon_parser"],
    "convert_to_fields",
    lambda x: x,
):
    import pytest_splunk_addon.standard_lib.addon_parser.transforms_parser

    importlib.reload(pytest_splunk_addon.standard_lib.addon_parser.transforms_parser)


from pytest_splunk_addon.standard_lib.addon_parser.transforms_parser import (
    TransformsParser,
)


output_to_build = {
    "ta_fiction_lookup": {
        "filename": "ta_fiction_splund_component.csv",
        "case_sensitive_match": "false",
    },
    "fiction-tsc-delim-fields": {
        "DELIMS": '","',
        "FIELDS": "day_id, event_id, end_time, start_time",
    },
    "fiction-tsc-sk-delim-format": {
        "SOURCE_KEY": "event_id",
        "DELIMS": '"="',
        "FIELDS": "server_contact_mode, dest",
    },
    "fiction-tsc-sk-regex-format": {
        "SOURCE_KEY": "component",
        "REGEX": "(.+)",
        "FORMAT": 'comp::"$1"',
    },
    "fiction-tsc-regex-format": {
        "REGEX": "(\w*)=(.*)",
        "FORMAT": "size1::$1 size2::$2",
    },
    "fiction-tsc-regex": {"REGEX": "group=(?<extractone>[^,]+)"},
    "fiction-tsc-regex-key-n": {
        "REGEX": "(?:^| )(?<_KEY_1>XXXXXX[^=]*)=(?! )(?<_VAL_1>.+?)(?=(?: [^ ]*(?<!\\)=|$))"
    },
    "fiction-tsc-regex-key-complex-n": {
        "REGEX": "c(c6a|f|n|s)(\d)Label=(?<_KEY_1>.+?)(?=(?: [^ ]*(?<!\\)=|$))(?=.*c\1\2=(?<_VAL_1>.+?)(?=(?: [^ ]*(?<!\\)=|$)))"
    },
}


def test_transforms_can_be_parsed_and_extracted(parser_instance):
    assert hasattr(
        parser_instance.transforms, "sects"
    ), "transforms can not be called or does not have sects attribute"


@pytest.mark.parametrize(
    "stanza, expected_outputs",
    [
        ("fiction-tsc-sk-delim-format", ["event_id", "server_contact_mode", "dest"]),
        ("fiction-tsc-regex-format", ["size1", "size2"]),
        ("fiction-tsc-regex", ["extractone"]),
    ],
)
def test_transforms_fields_can_be_parsed_and_returned(
    parsed_output, parser_instance, stanza, expected_outputs
):
    for i, event in enumerate(parser_instance.get_transform_fields(stanza)):
        assert event == expected_outputs[i], "expeceted event {} not found".format(
            expected_outputs[i]
        )


@pytest.fixture(scope="module")
def parsed_output(build_parsed_output):
    return build_parsed_output(output_to_build)


@pytest.fixture()
def parser_instance(parsed_output, parser):
    return parser(TransformsParser, "transforms_conf", parsed_output)
