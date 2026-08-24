import pytest
from unittest.mock import MagicMock, patch
from pytest_splunk_addon.addon_parser import Field
from pytest_splunk_addon.cim_tests.field_test_adapter import (
    FieldTestAdapter,
)


@pytest.fixture()
def field_mock(monkeypatch):
    field = MagicMock()
    monkeypatch.setattr("pytest_splunk_addon.cim_tests.field_test_adapter.Field", field)
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
    "multi_value, expected_output",
    [
        (True, "\n| nomv component_name"),
        (False, ""),
    ],
    ids=["multi_value", "single_value"],
)
def test_gen_validity_query(
    mocked_field_test_adapter,
    multi_value,
    expected_output,
):
    mocked_field_test_adapter.multi_value = multi_value
    assert mocked_field_test_adapter.gen_validity_query() == expected_output


def test_validity_query_already_exists(mocked_field_test_adapter):
    mocked_field_test_adapter.validity_query = "fake validity query"
    assert mocked_field_test_adapter.gen_validity_query() == "fake validity query"


@pytest.mark.parametrize(
    "expected_values, negative_values, expected_output",
    [
        ([], [], "component_validity"),
        (["*"], [], "component_validity"),
        (
            ["INFO", "WARN"],
            [],
            'if((component_validity) IN ("INFO", "WARN"), component_validity, null())',
        ),
        (
            [],
            ["", "-"],
            'if(NOT (component_validity) IN ("", "-"), component_validity, null())',
        ),
        (
            ["INFO", "WARN"],
            ["", "-"],
            'if((component_validity) IN ("INFO", "WARN") AND '
            'NOT (component_validity) IN ("", "-"), component_validity, null())',
        ),
    ],
    ids=["no_filters", "wildcard", "expected", "negative", "both"],
)
def test_get_validity_expression(
    mocked_field_test_adapter, expected_values, negative_values, expected_output
):
    mocked_field_test_adapter.expected_values = expected_values
    mocked_field_test_adapter.negative_values = negative_values

    assert mocked_field_test_adapter.get_validity_expression() == expected_output


def test_gen_stats_query():
    fta = FieldTestAdapter(
        Field(
            {
                "name": "component_name",
                "validity": "component_validity",
                "expected_values": [],
                "negative_values": [],
            }
        )
    )

    assert (
        fta.get_stats_query() == ", count(component_name) as component_name_count"
        ", count(eval(component_validity)) as component_name_valid_count"
        ", values(eval(if(isnull(component_validity), component_name, null()))) "
        "as component_name_invalid_values"
    )


def test_get_test_fields():
    fields = [Field({"name": "field_1"}), Field({"name": "field_2"})]

    test_fields = FieldTestAdapter.get_test_fields(fields)

    assert [field.name for field in test_fields] == ["field_1", "field_2"]
    assert all(isinstance(field, FieldTestAdapter) for field in test_fields)
