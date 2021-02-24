import pytest
from unittest.mock import MagicMock, mock_open


@pytest.fixture()
def open_mock(monkeypatch):
    open_mock = mock_open()
    monkeypatch.setattr("builtins.open", open_mock)
    return open_mock


@pytest.fixture()
def json_load_mock(monkeypatch):
    load_mock = MagicMock()
    monkeypatch.setattr("json.load", load_mock)
    return load_mock
