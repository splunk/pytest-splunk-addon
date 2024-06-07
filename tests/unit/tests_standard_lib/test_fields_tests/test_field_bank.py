import pytest
from unittest.mock import MagicMock
from pytest_splunk_addon.fields_tests.field_bank import FieldBank


@pytest.fixture()
def field_mock(monkeypatch):
    field_mock = MagicMock()
    field_mock.parse_fields.return_value = ["field1", "field_3"]
    monkeypatch.setattr(
        "pytest_splunk_addon.fields_tests.field_bank.Field", field_mock
    )
    return field_mock


@pytest.fixture()
def props_parser_mock(monkeypatch):
    props_parser_mock = MagicMock()
    props_parser_mock.get_list_of_sources.return_value = ["utility.log", "sys.log"]
    monkeypatch.setattr(
        "pytest_splunk_addon.fields_tests.field_bank.PropsParser",
        props_parser_mock,
    )
    return props_parser_mock


@pytest.mark.parametrize(
    "field_bank_path, json_value, expected_output",
    [
        (
            True,
            {"sourcetype::splunkd": ["field_1", "field_2", "field_3"]},
            [
                {
                    "stanza": "sourcetype::splunkd",
                    "stanza_type": "sourcetype",
                    "classname": "field_bank",
                    "fields": ["field1", "field_3"],
                }
            ],
        ),
        (
            True,
            {"source::(utility.log | sys.log)": ["field_1", "field_2", "field_3"]},
            [
                {
                    "stanza": "utility.log",
                    "stanza_type": "source",
                    "classname": "field_bank",
                    "fields": ["field1", "field_3"],
                },
                {
                    "stanza": "sys.log",
                    "stanza_type": "source",
                    "classname": "field_bank",
                    "fields": ["field1", "field_3"],
                },
            ],
        ),
        (
            True,
            {
                "sourcetype::splunkd": ["field_1", "field_2", "field_3"],
                "host::localhost": ["field_1", "field_2", "field_3"],
                "source::(utility.log | sys.log)": ["field_1", "field_2", "field_3"],
            },
            [
                {
                    "stanza": "sourcetype::splunkd",
                    "stanza_type": "sourcetype",
                    "classname": "field_bank",
                    "fields": ["field1", "field_3"],
                },
                {
                    "stanza": "utility.log",
                    "stanza_type": "source",
                    "classname": "field_bank",
                    "fields": ["field1", "field_3"],
                },
                {
                    "stanza": "sys.log",
                    "stanza_type": "source",
                    "classname": "field_bank",
                    "fields": ["field1", "field_3"],
                },
            ],
        ),
        (
            True,
            {"host::localhost": ["field_1", "field_2", "field_3"]},
            [],
        ),
        (
            False,
            {"sourcetype::splunkd": ["field_1", "field_2", "field_3"]},
            [],
        ),
    ],
)
def test_init_field_bank_tests(
    open_mock,
    json_load_mock,
    field_mock,
    props_parser_mock,
    field_bank_path,
    json_value,
    expected_output,
):
    json_load_mock.return_value = json_value
    out = list(FieldBank.init_field_bank_tests(field_bank_path))
    assert out == expected_output
