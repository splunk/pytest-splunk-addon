import pytest
from unittest.mock import mock_open, MagicMock


@pytest.fixture()
def open_mock(monkeypatch):
    open_mock = mock_open()
    monkeypatch.setattr("builtins.open", open_mock)
    return open_mock


@pytest.fixture()
def mock_object(monkeypatch):
    def create_mock_object(object_path, **kwargs):
        mo = MagicMock(**kwargs)
        monkeypatch.setattr(object_path, mo)
        return mo

    return create_mock_object


@pytest.fixture()
def os_path_join_file_mock(mock_object):
    os = mock_object("os.path.join")
    os.side_effect = lambda x, y: f"{x}/{y}"
    return os
