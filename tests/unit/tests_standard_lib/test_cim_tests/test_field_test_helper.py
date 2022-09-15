import pytest
from unittest.mock import patch, MagicMock
from collections import namedtuple
from pytest_splunk_addon.standard_lib.cim_tests.field_test_helper import FieldTestHelper
from pytest_splunk_addon.standard_lib.utilities.log_helper import get_table_output


field = namedtuple(
    "Field",
    ["name", "condition", "get_stats_query", "gen_validity_query", "get_properties"],
    defaults=("", "", None, None, None),
)


field_1 = field(name="field_1", gen_validity_query=lambda: True)
field_2 = field(name="field_2", gen_validity_query=lambda: True)


@pytest.fixture()
def field_test_adapter_mock(monkeypatch):
    fta_mock = MagicMock()
    fta_mock.get_test_fields.side_effect = lambda x: [
        f"{i}_return_value".upper() for i in x
    ]
    fta_mock.FIELD_COUNT = "{}_count"
    fta_mock.VALID_FIELD_COUNT = "{}_valid_count"
    fta_mock.INVALID_FIELD_VALUES = "{}_invalid_values"
    monkeypatch.setattr(
        "pytest_splunk_addon.standard_lib.cim_tests.field_test_helper.FieldTestAdapter",
        fta_mock,
    )


@pytest.fixture()
def mocked_field_test_helper():
    with patch.object(FieldTestHelper, "__init__", return_value=None):
        return FieldTestHelper()


@pytest.fixture()
def search_util_mock():
    su = MagicMock()
    su.getFieldValuesList.return_value = (
        f"SEARCH_UTIL_RETURN_VALUE_{i}" for i in range(3)
    )
    return su


@pytest.mark.parametrize(
    "args, expected_search_util, expected_fields, expected_intervals, expected_retries",
    [
        (
            ("fake_search_util", ["field_1", "field_2"]),
            "fake_search_util",
            ["FIELD_1_RETURN_VALUE", "FIELD_2_RETURN_VALUE"],
            10,
            4,
        ),
        (
            ("fake_search_util", ["unknown_field"], 20, 5),
            "fake_search_util",
            ["UNKNOWN_FIELD_RETURN_VALUE"],
            20,
            5,
        ),
    ],
)
def test_field_test_helper_instantiation(
    field_test_adapter_mock,
    args,
    expected_search_util,
    expected_fields,
    expected_intervals,
    expected_retries,
):
    fth = FieldTestHelper(*args)
    assert fth.search_util == expected_search_util
    assert fth.fields == expected_fields
    assert fth.interval == expected_intervals
    assert fth.retries == expected_retries


def test_test_field(mocked_field_test_helper, search_util_mock):
    record_property = MagicMock()
    mocked_field_test_helper.search = (
        "| search (index=* OR index=_internal)\n| search tag=tag_splunkd_fiction_one"
    )
    mocked_field_test_helper.search_util = search_util_mock
    mocked_field_test_helper.interval = 10
    mocked_field_test_helper.retries = 3
    with patch.object(
        FieldTestHelper, "_make_search_query"
    ) as make_search_mock, patch.object(
        FieldTestHelper, "_parse_result", return_value={"RESULT": "OK"}
    ) as parse_result_mock:
        assert mocked_field_test_helper.test_field("base_search", record_property) == {
            "RESULT": "OK"
        }
        make_search_mock.assert_called_once_with("base_search")
        parse_result_mock.assert_called_once_with(
            [
                "SEARCH_UTIL_RETURN_VALUE_0",
                "SEARCH_UTIL_RETURN_VALUE_1",
                "SEARCH_UTIL_RETURN_VALUE_2",
            ]
        )
        record_property.assert_called_once_with(
            "search",
            "| search (index=* OR index=_internal) | search tag=tag_splunkd_fiction_one",
        )


def test_gen_condition(mocked_field_test_helper):
    mocked_field_test_helper.fields = [
        field(condition="value > threshold_1"),
        field(condition=""),
        field(condition="value < threshold_2"),
        field(condition="value = threshold_3"),
    ]
    assert (
        mocked_field_test_helper._gen_condition()
        == "value > threshold_1 OR value < threshold_2 OR value = threshold_3"
    )


@pytest.mark.parametrize(
    "results, fields, expected_output",
    [
        (
            [
                {
                    "sourcetype": "splunkd",
                    "source": "/opt/splunk/var/log/splunk/health.log",
                    "event_count": "45",
                },
            ],
            None,
            [
                {
                    "sourcetype": "splunkd",
                    "source": "/opt/splunk/var/log/splunk/health.log",
                    "event_count": 45,
                },
            ],
        ),
        (
            [
                {
                    "sourcetype": "splunkd",
                    "source": "/opt/splunk/var/log/splunk/license_usage.log",
                    "event_count": "12",
                    "field_1_count": "8",
                    "field_1_valid_count": "5",
                    "field_2_count": "9",
                    "field_2_valid_count": "7",
                    "field_2_invalid_values": "2",
                },
            ],
            [field_1, field_2],
            [
                {
                    "sourcetype": "splunkd",
                    "source": "/opt/splunk/var/log/splunk/license_usage.log",
                    "event_count": 12,
                    "field_count": 8,
                    "valid_field_count": 5,
                    "invalid_values": "-",
                    "field": field_1,
                },
                {
                    "sourcetype": "splunkd",
                    "source": "/opt/splunk/var/log/splunk/license_usage.log",
                    "event_count": 12,
                    "field_count": 9,
                    "valid_field_count": 7,
                    "invalid_values": "2",
                    "field": field_2,
                },
            ],
        ),
    ],
)
def test_parse_result(
    field_test_adapter_mock, mocked_field_test_helper, results, fields, expected_output
):
    mocked_field_test_helper.fields = fields or []
    assert mocked_field_test_helper._parse_result(results) == expected_output


@pytest.mark.parametrize(
    "fields, expected_output",
    [
        (
            [
                field(
                    get_stats_query=lambda: ", count(alert) as alert_count",
                    gen_validity_query=lambda: "\n| eval alert_valid=alert",
                ),
                field(
                    get_stats_query=lambda: ", count(emergency) as emergency_count",
                    gen_validity_query=lambda: "\n| eval emergency_valid=emergency",
                ),
            ],
            "index=* event=alert OR event=emergency"
            "\n| eval alert_valid=alert"
            "\n| eval emergency_valid=emergency"
            " \n| stats count as event_count"
            ", count(alert) as alert_count"
            ", count(emergency) as emergency_count"
            " by sourcetype, source",
        ),
        (
            None,
            "index=* event=alert OR event=emergency"
            " \n| stats count as event_count"
            " by sourcetype, source",
        ),
    ],
)
def test_make_search_query(mocked_field_test_helper, fields, expected_output):
    mocked_field_test_helper.fields = fields or []
    with patch.object(
        FieldTestHelper, "_gen_condition", return_value="event=alert OR event=emergency"
    ):
        mocked_field_test_helper._make_search_query("index=*")
    assert (
        mocked_field_test_helper.search_event
        == "index=* event=alert OR event=emergency"
    )
    assert mocked_field_test_helper.search == expected_output


@pytest.mark.parametrize(
    "fields, expected_output",
    [
        (
            None,
            "Source, Sourcetype, Event Count\nutility.log, splunkd, 12\nsys.log, sc4s, 69\nSearch query:\nbase_search\n\nSearch query to copy:\nbase_search\n",
        ),
        (
            [
                field(name="field_1", get_properties=lambda: "field_1_properties"),
                field(
                    name="unknown_field",
                    get_properties=lambda: "unknown_field_properties",
                ),
            ],
            "Source, Sourcetype, Field, Event Count, Field Count, Invalid Field Count, Invalid Values\n"
            "utility.log, splunkd, field_1, 12, 10, 0, -\n"
            "sys.log, sc4s, unknown_field, 69, 9, 8, ['null', 'none']"
            "\nSearch query:\nbase_search\n\nSearch query to copy:\nbase_search\n"
            "\n\nProperties for the field :: field_1_properties"
            "\n\nProperties for the field :: unknown_field_properties",
        ),
    ],
)
def test_format_exc_message(mocked_field_test_helper, fields, expected_output):
    mocked_field_test_helper.parsed_result = [
        {
            "sourcetype": "splunkd",
            "source": "utility.log",
            "field": field(name="field_1"),
            "event_count": 12,
            "field_count": 10,
            "valid_field_count": 10,
            "invalid_values": [],
        },
        {
            "sourcetype": "sc4s",
            "source": "sys.log",
            "field": field(name="unknown_field"),
            "event_count": 69,
            "field_count": 9,
            "valid_field_count": 1,
            "invalid_values": ["null", "none"],
        },
    ]
    mocked_field_test_helper.fields = fields or []
    mocked_field_test_helper.search = "base_search"

    def table_output(headers, value_list):
        header = ", ".join(headers)
        rows = [", ".join([str(value) for value in row]) for row in value_list]
        output = "\n".join([header] + rows)
        return output

    with patch(
        "pytest_splunk_addon.standard_lib.cim_tests.field_test_helper.get_table_output",
        side_effect=table_output,
    ):
        assert mocked_field_test_helper.format_exc_message() == expected_output
