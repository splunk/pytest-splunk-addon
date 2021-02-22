import pytest
from unittest.mock import patch, MagicMock
from collections import namedtuple
from pytest_splunk_addon.standard_lib.cim_tests.field_test_helper import FieldTestHelper


field = namedtuple(
    "Field",
    ["name", "condition", "get_stats_query", "gen_validity_query"],
    defaults=("", "", None, None),
)


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
        "pytest_splunk_addon.standard_lib.cim_tests.field_test_helper.FieldTestAdapater",
        fta_mock,
    )


@pytest.fixture()
def mocked_field_test_helper():
    with patch.object(FieldTestHelper, "__init__", return_value=None):
        return FieldTestHelper()


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


def test_gen_condition(mocked_field_test_helper):
    mocked_field_test_helper.fields = [
        field(condition="value > min"),
        field(condition=""),
        field(condition="value < max"),
    ]
    assert mocked_field_test_helper._gen_condition() == "value > min OR value < max"


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
            [
                field(name="field_1", gen_validity_query=lambda: True),
                field(name="field_2", gen_validity_query=lambda: True),
            ],
            [
                {
                    "sourcetype": "splunkd",
                    "source": "/opt/splunk/var/log/splunk/license_usage.log",
                    "event_count": 12,
                    "field_count": 8,
                    "valid_field_count": 5,
                    "invalid_values": "-",
                    "field_name": "field_1",
                },
                {
                    "sourcetype": "splunkd",
                    "source": "/opt/splunk/var/log/splunk/license_usage.log",
                    "event_count": 12,
                    "field_count": 9,
                    "valid_field_count": 7,
                    "invalid_values": "2",
                    "field_name": "field_2",
                },
            ],
        ),
    ],
)
def test_parse_result(
    field_test_adapter_mock, mocked_field_test_helper, results, fields, expected_output
):
    mocked_field_test_helper.fields = fields or []
    if fields:
        for output in expected_output:
            for field in fields:
                if field.name == output["field_name"]:
                    output.update({"field": field})
                    output.pop("field_name")
                    break
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
