import pytest
from unittest.mock import mock_open, MagicMock


@pytest.fixture()
def open_mock(monkeypatch):
    open_mock = mock_open()
    monkeypatch.setattr("builtins.open", open_mock)
    return open_mock


@pytest.fixture()
def mock_object(monkeypatch):
    def create_mock_object(object_path):
        mo = MagicMock()
        monkeypatch.setattr(object_path, mo)
        return mo

    return create_mock_object
