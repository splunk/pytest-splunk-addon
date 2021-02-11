import pytest
from pytest_splunk_addon.standard_lib.event_ingestors.hec_raw_ingestor import (
    HECRawEventIngestor,
)
from urllib.parse import unquote


HEC_URI = "https://127.0.0.1:55238/services/collector"
HEADERS = {"Authorization": "Splunk 9b741d03-43e9-4164-908b-e09102327d22"}


@pytest.fixture()
def raw_ingestor():
    return HECRawEventIngestor({"session_headers": HEADERS, "splunk_hec_uri": HEC_URI})


def test_events_can_be_ingested(
    requests_mock, raw_ingestor, file_monitor_events, file_monitor_posts_sent
):
    requests_mock.post(f"{HEC_URI}/raw", request_headers=HEADERS)
    raw_ingestor.ingest(file_monitor_events, 1)
    assert requests_mock.call_count == 3
    sent_requests = [
        (unquote(str(req)), req.text) for req in requests_mock.request_history
    ]
    assert set(file_monitor_posts_sent) == set(sent_requests)


def test_exception_raised_when_event_ingestion_returns_error(
    requests_mock, raw_ingestor, file_monitor_events, caplog
):
    requests_mock.post(f"{HEC_URI}/raw", text="Not Found", status_code=404)
    pytest.raises(Exception, raw_ingestor.ingest, *(file_monitor_events, 1))
    assert (
        f"\n\nAn error occurred while data ingestion.\nStatus code: 404 \nReason: None \ntext:Not Found"
        in caplog.messages
    )
