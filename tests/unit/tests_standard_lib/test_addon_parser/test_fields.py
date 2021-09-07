from unittest.mock import MagicMock, call

import pytest

from pytest_splunk_addon.standard_lib.addon_parser.fields import (
    Field,
    convert_to_fields,
)

NAME = "name"
NAME1 = "Name1"
TYPE = "type"
TYPE1 = "Type1"
MULTI_VALUE = "multi_value"
MULTI_VALUE1 = "Multi_value1"
TEST_VALUE = "Test_values"
EXPECTED_VALUES = "expected_values"
EXPECTED_VALUES1 = "Expected_values1"
NEGATIVE_VALUES = "negative_values"
NEGATIVE_VALUES1 = "Negative_values1"
CONDITION = "condition"
CONDITION1 = "Condition1"
VALIDITY = "validity"
VALIDITY1 = "Validity1"

PROPERTIES = f"""{NAME1}
{TYPE}={TYPE1}
{MULTI_VALUE}={MULTI_VALUE1}
{CONDITION}={CONDITION1}
{VALIDITY}={VALIDITY1}
{EXPECTED_VALUES}={EXPECTED_VALUES1}
{NEGATIVE_VALUES}={NEGATIVE_VALUES1}"""


@pytest.fixture()
def field_json():
    return {
        NAME: NAME1,
        TYPE: TYPE1,
        MULTI_VALUE: MULTI_VALUE1,
        EXPECTED_VALUES: EXPECTED_VALUES1,
        NEGATIVE_VALUES: NEGATIVE_VALUES1,
        CONDITION: CONDITION1,
        VALIDITY: VALIDITY1,
    }


@pytest.fixture
def default_field(field_json):
    return Field(field_json=field_json)


@pytest.fixture
def field_mock(monkeypatch):
    field_mock = MagicMock()
    field_mock.return_value = TEST_VALUE
    monkeypatch.setattr(
        "pytest_splunk_addon.standard_lib.addon_parser.fields.Field", field_mock
    )
    return field_mock


def test_field_constructor(field_json):
    field = Field(field_json=field_json)
    assert field.name == NAME1
    assert field.type == TYPE1
    assert field.multi_value == MULTI_VALUE1
    assert field.expected_values == EXPECTED_VALUES1
    assert field.negative_values == NEGATIVE_VALUES1
    assert field.condition == CONDITION1
    assert field.validity == VALIDITY1

    for key in [
        TYPE,
        MULTI_VALUE,
        EXPECTED_VALUES,
        NEGATIVE_VALUES,
        CONDITION,
        VALIDITY,
    ]:
        field_json.pop(key)

    field = Field(field_json=field_json)
    assert field.name == NAME1
    assert field.type == "required"
    assert field.multi_value is False
    assert field.expected_values == ["*"]
    assert field.negative_values == ["-", ""]
    assert field.condition == ""
    assert field.validity == NAME1


def test_str(default_field):
    assert str(default_field) == NAME1


def test_get_type(default_field):
    assert default_field.get_type() == TYPE1


def test_parse_fields(default_field, field_mock):
    result = list(default_field.parse_fields([{"one": 1}, {"two": 2}], three=3, four=4))
    field_mock.assert_has_calls(
        [
            call({"three": 3, "four": 4, "one": 1}),
            call({"three": 3, "four": 4, "two": 2}),
        ]
    )
    assert result == 2 * [TEST_VALUE]


def test_get_properties(default_field):
    assert default_field.get_properties() == PROPERTIES


def test_convert_to_fields(field_mock):
    func = lambda: ["field1", "field2", "field3"]
    result = list(convert_to_fields(func)())
    field_mock.assert_has_calls(
        [call({"name": "field1"}), call({"name": "field2"}), call({"name": "field3"})]
    )
    assert result == 3 * [TEST_VALUE]
