import pytest
from unittest.mock import mock_open, MagicMock, patch
from collections import namedtuple
from pytest_splunk_addon.cim_tests.json_schema import JSONSchema


error = namedtuple("ValidationError", ["path", "instance", "message"])


@pytest.fixture()
def validator_mock(monkeypatch):
    with patch("pytest_splunk_addon.cim_tests.json_schema.Draft7Validator"):
        yield


@pytest.fixture(
    params=[
        [
            [error(["root", "not root"], {}, "error message")],
            "\nerror message for \\[root\\]\\[not root\\]",
        ],
        [
            [error(["root", "branch"], "", "error message")],
            "\nType mismatch: error message in property \\[root\\]\\[branch\\]",
        ],
        [
            [error(["root", "branch"], None, "error message")],
            "ValidationError",
        ],
    ]
)
def validator_mock_with_error(request):
    d7v_mock = MagicMock()
    d7v_mock.return_value = d7v_mock
    d7v_mock.iter_errors.return_value = request.param[0]
    with patch(
        "pytest_splunk_addon.cim_tests.json_schema.Draft7Validator",
        d7v_mock,
    ):
        yield request.param[1]


@pytest.fixture()
def validator_mock_raises_decode_error():
    doc = MagicMock()
    doc.return_value = doc
    doc.count.return_value = 5
    doc.rfind.return_value = 2
    from json.decoder import JSONDecodeError

    with patch(
        "pytest_splunk_addon.cim_tests.json_schema.Draft7Validator",
        MagicMock(side_effect=JSONDecodeError("error", doc, 9)),
    ):
        yield


def test_parse_data_model_returns_parsed_json_data(
    open_mock, json_load_mock, validator_mock
):
    json_load_mock.side_effect = [{"key1": "val1"}, {"key2": "val2"}]
    assert JSONSchema.parse_data_model("fake_path") == {"key2": "val2"}


def test_parse_data_model_error(open_mock, json_load_mock, validator_mock_with_error):
    with pytest.raises(Exception, match=validator_mock_with_error):
        JSONSchema.parse_data_model("fake_path")


def test_parse_data_model_decode_error(
    open_mock, json_load_mock, validator_mock_raises_decode_error
):
    with pytest.raises(
        Exception, match="error: line 6 column 7 \\(char 9\\) in file fake_path"
    ):
        JSONSchema.parse_data_model("fake_path")
