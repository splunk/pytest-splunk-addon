import pytest
from pytest_splunk_addon.standard_lib.event_ingestors.hec_event_ingestor import (
    HECEventIngestor,
)
from pytest_splunk_addon.standard_lib.event_ingestors.hec_metric_ingestor import (
    HECMetricEventIngestor,
)
from pytest_splunk_addon.standard_lib.event_ingestors.hec_raw_ingestor import (
    HECRawEventIngestor,
)
from urllib.parse import unquote


HEC_URI = "https://127.0.0.1:55238/services/collector"
HEADERS = {"Authorization": "Splunk 9b741d03-43e9-4164-908b-e09102327d22"}


@pytest.fixture()
def hec_event_ingestor():
    return HECEventIngestor({"session_headers": HEADERS, "splunk_hec_uri": HEC_URI})


@pytest.fixture()
def hec_metric_event_ingestor():
    return HECMetricEventIngestor(
        {"session_headers": HEADERS, "splunk_hec_uri": HEC_URI}
    )


@pytest.fixture()
def hec_raw_event_ingestor():
    return HECRawEventIngestor({"session_headers": HEADERS, "splunk_hec_uri": HEC_URI})


@pytest.fixture()
def ingestors(
    hec_event_ingestor,
    modinput_events,
    modinput_posts_sent,
    hec_metric_event_ingestor,
    metric_events,
    metric_posts_sent,
    hec_raw_event_ingestor,
    file_monitor_events,
    file_monitor_posts_sent,
):
    return {
        "hec_event_ingestor": {
            "ingestor": hec_event_ingestor,
            "events": modinput_events,
            "posts": modinput_posts_sent,
        },
        "hec_metric_event_ingestor": {
            "ingestor": hec_metric_event_ingestor,
            "events": metric_events,
            "posts": metric_posts_sent,
        },
        "hec_raw_event_ingestor": {
            "ingestor": hec_raw_event_ingestor,
            "events": file_monitor_events,
            "posts": file_monitor_posts_sent,
        },
    }


@pytest.mark.parametrize(
    "ingestor_name, url, call_count",
    [
        ("hec_event_ingestor", f"{HEC_URI}/event", 1),
        ("hec_metric_event_ingestor", HEC_URI, 1),
        ("hec_raw_event_ingestor", f"{HEC_URI}/raw", 3),
    ],
)
def test_events_can_be_ingested(
    requests_mock, ingestors, ingestor_name, url, call_count
):
    requests_mock.post(url, request_headers=HEADERS)
    ingestor = ingestors[ingestor_name]
    ingestor["ingestor"].ingest(ingestor["events"], 1)
    assert requests_mock.call_count == call_count
    sent_requests = [
        (unquote(str(req)), req.text) for req in requests_mock.request_history
    ]
    assert set(ingestor["posts"]) == set(sent_requests)


@pytest.mark.parametrize(
    "ingestor_name, url, check_logger",
    [
        ("hec_event_ingestor", f"{HEC_URI}/event", True),
        ("hec_metric_event_ingestor", HEC_URI, False),
        ("hec_raw_event_ingestor", f"{HEC_URI}/raw", True),
    ],
)
def test_exception_raised_when_event_ingestion_returns_error(
    requests_mock, ingestors, caplog, ingestor_name, url, check_logger
):
    requests_mock.post(url, text="Not Found", status_code=404)
    ingestor = ingestors[ingestor_name]
    with pytest.raises(Exception, match="An error occurred while data ingestion"):
        ingestor["ingestor"].ingest(ingestor["events"], 1)
    if check_logger:
        assert (
            f"\n\nAn error occurred while data ingestion.\nStatus code: 404 \nReason: None \ntext:Not Found"
            in caplog.messages
        )
