import importlib
import pytest
from unittest.mock import patch, mock_open, PropertyMock
from collections import namedtuple

with patch(
    "pytest_splunk_addon.standard_lib.addon_parser.convert_to_fields",
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
        "REGEX": r"(\w*)=(.*)",
        "FORMAT": "size1::$1 size2::$2",
    },
    "fiction-tsc-regex": {"REGEX": "group=(?<extractone>[^,]+)"},
    "fiction-tsc-regex-key-n": {
        "REGEX": "(?:^| )(?<_KEY_1>XXXXXX[^=]*)=(?! )(?<_VAL_1>.+?)(?=(?: [^ ]*(?<!\\)=|$))"
    },
    "fiction-tsc-regex-key-complex-n": {
        "REGEX": "c(c6a|f|n|s)(\\d)Label=(?<_KEY_1>.+?)(?=(?: [^ ]*(?<!\\)=|$))(?=.*c\1\2=(?<_VAL_1>.+?)(?=(?: [^ ]*(?<!\\)=|$)))"
    },
}

csv_fieldnames = [
    "component ",
    "fiction_context_test",
    " aliasone",
    " status_test",
    " test_name",
    " type",
    " status.test",
    " fiction_context_test1",
    " fiction_context_test2",
    " status2",
]
csv_reader = namedtuple("DictReader", ["fieldnames"])


@pytest.fixture(scope="module")
def parsed_output(build_parsed_output):
    return build_parsed_output(output_to_build)


@pytest.fixture()
def parser_instance(parsed_output, parser):
    return parser(TransformsParser, "transforms_conf", parsed_output)


@pytest.fixture()
def parser_with_empty_transforms_mocked(parser):
    with patch.object(
        TransformsParser, "transforms", new_callable=PropertyMock, return_value=None
    ):
        yield parser(TransformsParser, "transforms_conf", {})


@pytest.fixture()
def parser_with_mocked_transforms(configuration_file, parser, parsed_output):
    conf_file = configuration_file(headers=[], sects=parsed_output, errors=[])
    with patch.object(
        TransformsParser,
        "transforms",
        new_callable=PropertyMock,
        return_value=conf_file,
    ):
        yield parser(TransformsParser, "transforms_conf", {})


def test_transforms_can_be_parsed_and_extracted(parser_instance):
    assert list(parser_instance.transforms.sects.keys()) == [
        "ta_fiction_lookup",
        "fiction-tsc-delim-fields",
        "fiction-tsc-sk-delim-format",
        "fiction-tsc-sk-regex-format",
        "fiction-tsc-regex-format",
        "fiction-tsc-regex",
        "fiction-tsc-regex-key-n",
        "fiction-tsc-regex-key-complex-n",
    ], "tags can not be called or does not have sects attribute"


def test_transforms_calls_app_transforms_conf(parser_instance):
    _ = parser_instance.transforms
    parser_instance.app.transforms_conf.assert_called_once()


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
    for event, expected_output in zip(
        parser_instance.get_transform_fields(stanza), expected_outputs
    ):
        assert event == expected_output, "expeceted event {} not found".format(
            expected_output
        )


def test_get_lookup_csv_fields(parser_instance):
    with patch("builtins.open", mock_open()):
        csv_reader.fieldnames = csv_fieldnames
        with patch("csv.DictReader", return_value=csv_reader):
            for i, fieldname in enumerate(
                parser_instance.get_lookup_csv_fields("ta_fiction_lookup")
            ):
                assert fieldname == csv_fieldnames[i].strip()


def test_no_transforms_config_file(parser_instance):
    parser_instance.app.transforms_conf.side_effect = OSError
    assert (
        parser_instance.transforms is None
    ), "transforms created when no config file exists"


def test_no_transforms_returned_when_empty_config_file(
    parser_with_empty_transforms_mocked,
):
    output = [
        transform
        for transform in parser_with_empty_transforms_mocked.get_transform_fields(
            "dummy_stanza"
        )
        if transform
    ]
    assert output == [], "transforms returned when no config file exists"


def test_stanza_does_not_exist_in_transforms(parser_with_mocked_transforms, caplog):
    for result in parser_with_mocked_transforms.get_transform_fields("dummy_stanza"):
        assert result is None, "non existing stanza results returned"
    assert caplog.messages == [
        "The stanza dummy_stanza does not exists in transforms.conf."
    ]


def test_no_lookup_returned_when_empty_config_file(parser_with_empty_transforms_mocked):
    output = [
        lookup
        for lookup in parser_with_empty_transforms_mocked.get_lookup_csv_fields(
            "dummy_stanza"
        )
        if lookup
    ]
    assert output == [], "lookups returned when no config file exists"


def test_lookup_files_does_not_exist(parser_with_mocked_transforms, caplog):
    with patch("builtins.open", mock_open()) as mocked_open:
        mocked_open.side_effect = OSError("no such file")
        for result in parser_with_mocked_transforms.get_lookup_csv_fields(
            "ta_fiction_lookup"
        ):
            assert result is None, "non existing stanza results returned"
    assert caplog.messages == [
        "Could not read the lookup file, skipping test. error=no such file"
    ]
