import pytest
from unittest.mock import MagicMock, call
from pytest_splunk_addon.event_ingestors.sc4s_event_ingestor import (
    SC4SEventIngestor,
)

required_config = {
    "session_headers": {"Authorization": "Splunk 9b741d03-43e9-4164-908b-e09102327d22"},
    "splunk_hec_uri": "https://127.0.0.1:55675/services/collector",
    "sc4s_host": "127.0.0.1",
    "sc4s_port": 55730,
}


@pytest.fixture()
def sc4s_ingestor():
    return SC4SEventIngestor(required_config)


@pytest.fixture
def socket_mock(monkeypatch):
    socket_mock = MagicMock()
    socket_mock.return_value = socket_mock
    monkeypatch.setattr(
        "socket.socket",
        socket_mock,
    )
    monkeypatch.setattr(
        "socket.AF_INET",
        "AF_INET",
    )
    monkeypatch.setattr(
        "socket.SOCK_STREAM",
        "SOCK_STREAM",
    )
    return socket_mock


@pytest.fixture()
def sleep_mock(monkeypatch):
    monkeypatch.setattr(
        "pytest_splunk_addon.event_ingestors.sc4s_event_ingestor.sleep",
        MagicMock(),
    )


def test_sc4s_data_can_be_ingested(socket_mock, sc4s_ingestor, sc4s_events):
    sc4s_ingestor.ingest(sc4s_events, 20)
    assert socket_mock.call_count == 2
    socket_mock.assert_has_calls(
        [call("AF_INET", "SOCK_STREAM"), call("AF_INET", "SOCK_STREAM")], any_order=True
    )
    assert socket_mock.connect.call_count == 2
    socket_mock.connect.assert_has_calls(
        [call(("127.0.0.1", 55730)), call(("127.0.0.1", 55730))]
    )
    assert socket_mock.sendall.call_count == 2
    assert socket_mock.close.call_count == 2


def test_exception_raised_when_sc4s_socket_can_not_be_opened(
    socket_mock, sleep_mock, sc4s_ingestor, sc4s_events, caplog
):
    socket_mock.connect.side_effect = Exception
    pytest.raises(Exception, sc4s_ingestor.ingest, *(sc4s_events, 20))
    assert "Failed to ingest event with SC4S 91 times" in caplog.messages
    assert socket_mock.connect.call_count == socket_mock.close.call_count == 91


def test_exception_raised_when_sc4s_event_sent(
    socket_mock, sleep_mock, sc4s_ingestor, sc4s_events, caplog
):
    socket_mock.sendall.side_effect = Exception("Send data fail")
    sc4s_ingestor.ingest(sc4s_events, 20)
    assert "Send data fail" in caplog.messages
    assert socket_mock.connect.call_count == socket_mock.close.call_count == 2
