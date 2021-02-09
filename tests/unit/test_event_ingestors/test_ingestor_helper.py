import importlib
import pytest
from unittest.mock import patch


EVENT_INGESTOR_PATH = "pytest_splunk_addon.standard_lib.event_ingestors"
HEC_EVENT_INGESTOR_RETURN_VALUE = "hec_event_ingestor_return_value"
HEC_RAW_EVENT_INGESTOR_RETURN_VALUE = "hec_raw_event_ingestor_return_value"
HEC_METRIC_EVENT_INGESTOR_RETURN_VALUE = "hec_metric_event_ingestor_return_value"
SC4S_EVENT_INGESTOR_RETURN_VALUE = "sc4s_event_ingestor_return_value"


@pytest.fixture()
def event_ingestor():
    with patch(f"{EVENT_INGESTOR_PATH}.hec_event_ingestor.HECEventIngestor") as hec_event_mock, \
         patch(f"{EVENT_INGESTOR_PATH}.hec_raw_ingestor.HECRawEventIngestor") as hec_raw_event_mock, \
         patch(f"{EVENT_INGESTOR_PATH}.hec_metric_ingestor.HECMetricEventIngestor") as hec_metric_event_mock, \
         patch(f"{EVENT_INGESTOR_PATH}.sc4s_event_ingestor.SC4SEventIngestor") as sc4s_event_mock:

        hec_event_mock.return_value = HEC_EVENT_INGESTOR_RETURN_VALUE
        hec_raw_event_mock.return_value = HEC_RAW_EVENT_INGESTOR_RETURN_VALUE
        hec_metric_event_mock.return_value = HEC_METRIC_EVENT_INGESTOR_RETURN_VALUE
        sc4s_event_mock.return_value = SC4S_EVENT_INGESTOR_RETURN_VALUE

        mocks = {HEC_EVENT_INGESTOR_RETURN_VALUE: hec_event_mock,
                 HEC_RAW_EVENT_INGESTOR_RETURN_VALUE: hec_raw_event_mock,
                 HEC_METRIC_EVENT_INGESTOR_RETURN_VALUE: hec_metric_event_mock,
                 SC4S_EVENT_INGESTOR_RETURN_VALUE: sc4s_event_mock}

        import pytest_splunk_addon.standard_lib.event_ingestors
        import pytest_splunk_addon.standard_lib.event_ingestors.ingestor_helper
        importlib.reload(pytest_splunk_addon.standard_lib.event_ingestors)
        importlib.reload(pytest_splunk_addon.standard_lib.event_ingestors.ingestor_helper)

        return pytest_splunk_addon.standard_lib.event_ingestors.ingestor_helper, mocks


@pytest.mark.parametrize(
    "ingest_method, expected_output",
    [
        ("modinput", HEC_EVENT_INGESTOR_RETURN_VALUE),
        ("windows_input", HEC_EVENT_INGESTOR_RETURN_VALUE),
        ("file_monitor", HEC_RAW_EVENT_INGESTOR_RETURN_VALUE),
        ("scripted_input", HEC_RAW_EVENT_INGESTOR_RETURN_VALUE),
        ("hec_metric", HEC_METRIC_EVENT_INGESTOR_RETURN_VALUE),
        ("syslog_tcp", SC4S_EVENT_INGESTOR_RETURN_VALUE),
        ("default", HEC_RAW_EVENT_INGESTOR_RETURN_VALUE)
    ],
)
def test_ingestor_can_be_obtained(event_ingestor, ingest_method, expected_output):
    ingestor, event_mock = event_ingestor
    assert ingestor.IngestorHelper.get_event_ingestor(ingest_method, "ingest_meta_data") == expected_output
    assert event_mock[expected_output].has_calls("ingest_meta_data")


@pytest.mark.parametrize(
    "ingest_method",
    [
        "syslog_udp",
        "new_ingest_method",
    ],
)
def test_non_implemented_ingestor_can_not_be_obtained(event_ingestor, ingest_method):
    ingestor, _ = event_ingestor
    pytest.raises(TypeError, ingestor.IngestorHelper.get_event_ingestor, *(ingest_method, "ingest_meta_data"))

