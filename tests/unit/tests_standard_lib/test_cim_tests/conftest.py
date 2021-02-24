import pytest
from unittest.mock import MagicMock, mock_open


@pytest.fixture()
def field_mock(monkeypatch):
    field = MagicMock()
    monkeypatch.setattr(
        "pytest_splunk_addon.standard_lib.cim_tests.field_test_adapter.Field", field
    )
    return field


@pytest.fixture()
def open_mock(monkeypatch):
    open_mock = mock_open()
    monkeypatch.setattr("builtins.open", mock_open())
    return open_mock


@pytest.fixture()
def json_load_mock(monkeypatch):
    load_mock = MagicMock()
    monkeypatch.setattr("json.load", load_mock)
    return load_mock
