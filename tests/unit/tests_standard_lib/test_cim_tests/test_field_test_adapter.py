import pytest
from unittest.mock import MagicMock, patch
from pytest_splunk_addon.cim_tests.field_test_adapter import (
    FieldTestAdapter,
)


@pytest.fixture()
def field_mock(monkeypatch):
    field = MagicMock()
    monkeypatch.setattr(
        "pytest_splunk_addon.cim_tests.field_test_adapter.Field", field
    )
    return field


@pytest.fixture()
def field_instance():
    field = MagicMock()
    field.field_key_1 = 1
    field.field_key_2 = "2"
    field.__str__.return_value = "test_field"
    return field


@pytest.fixture()
def mocked_field_test_adapter(field_instance):
    with patch.object(FieldTestAdapter, "__init__", return_value=None), patch.object(
        FieldTestAdapter, "get_query_from_values", side_effect=lambda x: ", ".join(x)
    ):
        fta = FieldTestAdapter("field")
        fta.valid_field = "component_valid"
        fta.invalid_field = "component_invalid"
        fta.validity_query = None
        fta.name = "component_name"
        fta.validity = "component_validity"
        yield fta


def test_get_query_from_values():
    assert (
        FieldTestAdapter.get_query_from_values(["field1", "field2", "unknown_field"])
        == '\\"field1\\", \\"field2\\", \\"unknown_field\\"'
    )


def test_field_test_adapter_instantiation(field_mock, field_instance):
    fta = FieldTestAdapter(field_instance)
    assert fta.field_key_1 == 1
    assert fta.field_key_2 == "2"
    assert fta.valid_field == "test_field_valid"
    assert fta.invalid_field == "test_field_invalid"
    assert fta.validity_query is None


@pytest.mark.parametrize(
    "multi_value, expected_values, negative_values, expected_output",
    [
        (
            True,
            None,
            None,
            f"\n| nomv component_name"
            f"\n| eval component_valid=component_validity"
            f"\n| eval component_invalid=if(isnull(component_valid), component_name, null())",
        ),
        (
            False,
            ["INFO", "WARN", "ERROR", "FATAL"],
            None,
            f"\n| eval component_valid=component_validity"
            f'\n| eval component_valid=if(searchmatch("component_valid IN '
            f'(INFO, WARN, ERROR, FATAL)"), component_valid, null())'
            f"\n| eval component_invalid=if(isnull(component_valid), component_name, null())",
        ),
        (
            False,
            None,
            ["", "-", "unknown", "null", "(null)"],
            f"\n| eval component_valid=component_validity"
            f'\n| eval component_valid=if(searchmatch("component_valid IN '
            f'(, -, unknown, null, (null))"), null(), component_valid)'
            f"\n| eval component_invalid=if(isnull(component_valid), component_name, null())",
        ),
        (
            True,
            ["INFO", "WARN", "ERROR", "FATAL"],
            ["", "-", "unknown", "null", "(null)"],
            f"\n| nomv component_name"
            f"\n| eval component_valid=component_validity"
            f'\n| eval component_valid=if(searchmatch("component_valid IN '
            f'(INFO, WARN, ERROR, FATAL)"), component_valid, null())'
            f'\n| eval component_valid=if(searchmatch("component_valid IN '
            f'(, -, unknown, null, (null))"), null(), component_valid)'
            f"\n| eval component_invalid=if(isnull(component_valid), component_name, null())",
        ),
    ],
    ids=["multi_value", "expected_values", "negative_values", "all"],
)
def test_gen_validity_query(
    mocked_field_test_adapter,
    multi_value,
    expected_values,
    negative_values,
    expected_output,
):
    mocked_field_test_adapter.multi_value = multi_value
    mocked_field_test_adapter.expected_values = expected_values or []
    mocked_field_test_adapter.negative_values = negative_values or []
    assert mocked_field_test_adapter.gen_validity_query() == expected_output


def test_validity_query_already_exists(mocked_field_test_adapter):
    mocked_field_test_adapter.validity_query = "fake validity query"
    assert mocked_field_test_adapter.gen_validity_query() == "fake validity query"


def test_gen_stats_query():
    with patch.object(FieldTestAdapter, "__init__", return_value=None), patch.object(
        FieldTestAdapter, "gen_validity_query", return_value=True
    ):
        fta = FieldTestAdapter("field")
        fta.name = "component_name"
        fta.valid_field = "valid_field"
        fta.invalid_field = "invalid_field"
        assert (
            fta.get_stats_query() == f", count(component_name) as component_name_count"
            f", count(valid_field) as component_name_valid_count"
            f", values(invalid_field) as component_name_invalid_values"
        )


def test_get_test_fields():
    with patch.object(
        FieldTestAdapter,
        "__new__",
        side_effect=lambda cls, f: f"{f}_return_value".upper(),
    ):
        assert FieldTestAdapter.get_test_fields(["field_1", "field_2"]) == [
            "FIELD_1_RETURN_VALUE",
            "FIELD_2_RETURN_VALUE",
        ]
