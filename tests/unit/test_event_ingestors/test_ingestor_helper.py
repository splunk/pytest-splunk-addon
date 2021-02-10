import importlib
import pytest
from unittest.mock import patch, MagicMock, call
from recordtype import recordtype
import pytest_splunk_addon.standard_lib.event_ingestors as event_ingestors


EVENT_INGESTOR_PATH = "pytest_splunk_addon.standard_lib.event_ingestors"
HEC_EVENT_INGESTOR_RETURN_VALUE = "hec_event_ingestor_return_value"
HEC_RAW_EVENT_INGESTOR_RETURN_VALUE = "hec_raw_event_ingestor_return_value"
HEC_METRIC_EVENT_INGESTOR_RETURN_VALUE = "hec_metric_event_ingestor_return_value"
SC4S_EVENT_INGESTOR_RETURN_VALUE = "sc4s_event_ingestor_return_value"


SampleEvent = recordtype("SampleEvent", ["event", "metadata", "sample_name"],)


@pytest.fixture()
def ingestors_mocks():
    with patch(
        f"{EVENT_INGESTOR_PATH}.hec_event_ingestor.HECEventIngestor"
    ) as hec_event_mock, patch(
        f"{EVENT_INGESTOR_PATH}.hec_raw_ingestor.HECRawEventIngestor"
    ) as hec_raw_event_mock, patch(
        f"{EVENT_INGESTOR_PATH}.hec_metric_ingestor.HECMetricEventIngestor"
    ) as hec_metric_event_mock, patch(
        f"{EVENT_INGESTOR_PATH}.sc4s_event_ingestor.SC4SEventIngestor"
    ) as sc4s_event_mock:

        hec_event_mock.return_value = HEC_EVENT_INGESTOR_RETURN_VALUE
        hec_raw_event_mock.return_value = HEC_RAW_EVENT_INGESTOR_RETURN_VALUE
        hec_metric_event_mock.return_value = HEC_METRIC_EVENT_INGESTOR_RETURN_VALUE
        sc4s_event_mock.return_value = SC4S_EVENT_INGESTOR_RETURN_VALUE

        yield {
            HEC_EVENT_INGESTOR_RETURN_VALUE: hec_event_mock,
            HEC_RAW_EVENT_INGESTOR_RETURN_VALUE: hec_raw_event_mock,
            HEC_METRIC_EVENT_INGESTOR_RETURN_VALUE: hec_metric_event_mock,
            SC4S_EVENT_INGESTOR_RETURN_VALUE: sc4s_event_mock,
        }


@pytest.fixture()
def ingestor_helper(ingestors_mocks):
    importlib.reload(event_ingestors)
    importlib.reload(event_ingestors.ingestor_helper)

    return event_ingestors.ingestor_helper.IngestorHelper


@pytest.fixture()
def get_ingestor_mock():
    with patch.object(
        event_ingestors.ingestor_helper.IngestorHelper,
        "get_event_ingestor",
        new=MagicMock(),
    ) as ingestor_mock:
        ingestor_mock.return_value = ingestor_mock
        yield ingestor_mock


@pytest.fixture()
def tokenized_events():
    return [
        SampleEvent(
            event="host=test-host-file_monitor_host_prefix.sample-2",
            metadata={
                "interval": "60",
                "earliest": "-60s",
                "latest": "now",
                "source": "pytest-splunk-addon:file_monitor",
                "sourcetype": "test:indextime:file_monitor_host_prefix",
                "input_type": "file_monitor",
                "host_type": "event",
                "host_prefix": "test-",
                "sourcetype_to_search": "test:indextime:file_monitor_host_prefix",
                "timestamp_type": "event",
                "sample_count": "2",
                "host": "file_monitor_host_prefix.sample",
                "expected_event_count": 1,
            },
            sample_name="file_monitor_host_prefix.sample",
        ),
        SampleEvent(
            event="test_modinput_1 host=modinput_host_event_time_plugin.samples_1",
            metadata={
                "sourcetype": "test:indextime:sourcetype:modinput_host_event_time_plugin",
                "host_type": "event",
                "input_type": "modinput",
                "source": "pytest-splunk-addon:modinput",
                "sourcetype_to_search": "test:indextime:sourcetype:modinput_host_event_time_plugin",
                "timestamp_type": "plugin",
                "sample_count": "2",
                "host": "modinput_host_event_time_plugin.samples_1",
                "expected_event_count": 2,
            },
            sample_name="modinput_host_event_time_plugin.samples",
        ),
        SampleEvent(
            event="test_modinput_2 host=modinput_host_event_time_plugin.samples_2",
            metadata={
                "sourcetype": "test:indextime:sourcetype:modinput_host_event_time_plugin",
                "host_type": "event",
                "input_type": "modinput",
                "source": "pytest-splunk-addon:modinput",
                "sourcetype_to_search": "test:indextime:sourcetype:modinput_host_event_time_plugin",
                "timestamp_type": "plugin",
                "sample_count": "2",
                "host": "modinput_host_event_time_plugin.samples_2",
                "expected_event_count": 2,
            },
            sample_name="modinput_host_event_time_plugin.samples",
        ),
    ]


@pytest.fixture()
def requirement_events():
    return [
        SampleEvent(
            event="requirement event",
            metadata={
                "source": "requirement source",
                "sourcetype": "requirement source type",
                "input_type": "file_monitor",
                "host_type": "event",
                "host_prefix": "test-",
                "sourcetype_to_search": "test:indextime:requirement",
                "timestamp_type": "event",
                "sample_count": "2",
                "host": "requirement_host_prefix.sample",
                "expected_event_count": 1,
            },
            sample_name="requirement_test",
        ),
    ]


@pytest.fixture
def sample_mock(monkeypatch, tokenized_events):
    sample_mock = MagicMock()
    sample_mock.return_value = sample_mock
    sample_mock.get_samples.return_value = {
        "conf_name": "psa-data-gen",
        "tokenized_events": tokenized_events,
    }
    monkeypatch.setattr(
        "pytest_splunk_addon.standard_lib.event_ingestors.ingestor_helper.SampleXdistGenerator",
        sample_mock,
    )
    return sample_mock


@pytest.fixture()
def requirement_mock(monkeypatch):
    req_mock = MagicMock()
    req_mock.return_value = req_mock
    req_mock.get_events.return_value = {
        "conf_name": "psa-data-gen",
        "tokenized_events": tokenized_events,
    }
    monkeypatch.setattr(
        "pytest_splunk_addon.standard_lib.event_ingestors.ingestor_helper.RequirementEventIngestor",
        req_mock,
    )
    return req_mock


@pytest.mark.parametrize(
    "ingest_method, expected_output",
    [
        ("modinput", HEC_EVENT_INGESTOR_RETURN_VALUE),
        ("windows_input", HEC_EVENT_INGESTOR_RETURN_VALUE),
        ("file_monitor", HEC_RAW_EVENT_INGESTOR_RETURN_VALUE),
        ("scripted_input", HEC_RAW_EVENT_INGESTOR_RETURN_VALUE),
        ("hec_metric", HEC_METRIC_EVENT_INGESTOR_RETURN_VALUE),
        ("syslog_tcp", SC4S_EVENT_INGESTOR_RETURN_VALUE),
        ("default", HEC_RAW_EVENT_INGESTOR_RETURN_VALUE),
    ],
)
def test_ingestor_can_be_obtained(
    ingestor_helper, ingestors_mocks, ingest_method, expected_output
):
    assert (
        ingestor_helper.get_event_ingestor(ingest_method, "ingest_meta_data")
        == expected_output
    )
    assert ingestors_mocks[expected_output].has_calls("ingest_meta_data")


@pytest.mark.parametrize(
    "ingest_method",
    [
        "syslog_udp",
        "new_ingest_method",
    ],
)
def test_non_implemented_ingestor_can_not_be_obtained(ingestor_helper, ingest_method):
    pytest.raises(
        TypeError,
        ingestor_helper.get_event_ingestor,
        *(ingest_method, "ingest_meta_data"),
    )


def test_events_can_be_ingested(get_ingestor_mock, sample_mock, tokenized_events):
    event_ingestors.ingestor_helper.IngestorHelper.ingest_events(
        ingest_meta_data={},
        addon_path="fake_path",
        config_path="tests/unit/event_ingestors",
        thread_count=20,
        store_events=False,
        run_requirement_test=False,
    )
    assert get_ingestor_mock.call_count == 2
    get_ingestor_mock.assert_has_calls(
        [call("file_monitor", {}), call("modinput", {})], any_order=True
    )
    assert get_ingestor_mock.ingest.call_count == 2
    get_ingestor_mock.ingest.has_calls(
        [tokenized_events[0], 20], [[tokenized_events[1], tokenized_events[2]], 20]
    )


def test_requirement_tests_can_be_performed(get_ingestor_mock, sample_mock, requirement_mock, requirement_events):
    event_ingestors.ingestor_helper.IngestorHelper.ingest_events(
        ingest_meta_data={},
        addon_path="fake_path",
        config_path="tests/unit/event_ingestors",
        thread_count=20,
        store_events=False,
        run_requirement_test=True,
    )
    requirement_mock.assert_called_once_with('fake_path')
    requirement_mock.get_events.assert_called_once
    assert get_ingestor_mock.ingest.call_count == 3
    get_ingestor_mock.ingest.has_calls([requirement_events, 20])
