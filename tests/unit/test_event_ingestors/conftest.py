import pytest
from recordtype import recordtype
from .test_hec_event_metric_raw_ingestor import HEC_URI

SampleEvent = recordtype(
    "SampleEvent",
    ["event", "metadata", "sample_name", ("key_fields", None), ("time_values", None)],
)


@pytest.fixture()
def modinput_events():
    return [
        SampleEvent(
            event="test_modinput_1 host=modinput_host_event_time_plugin.samples_1",
            key_fields={"host": ["modinput_host_event_time_plugin.samples_1"]},
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
            key_fields={"host": ["modinput_host_event_time_plugin.samples_2"]},
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
        SampleEvent(
            event="fake event nothing happened",
            key_fields={},
            metadata={
                "host_type": "plugin",
                "input_type": "modinput",
                "index": "fake_index",
                "timestamp_type": "event",
                "host": "fake host",
            },
            sample_name="fake.samples",
            time_values=[1234.5678, 1234.5679],
        ),
    ]


@pytest.fixture()
def modinput_posts_sent():
    return [
        (
            f"POST {HEC_URI}/event",
            "[{"
            '"sourcetype": "test:indextime:sourcetype:modinput_host_event_time_plugin", '
            '"source": "pytest-splunk-addon:modinput", '
            '"event": "test_modinput_1 host=modinput_host_event_time_plugin.samples_1", '
            '"index": "main", '
            '"host": "modinput_host_event_time_plugin.samples_1"'
            "}, {"
            '"sourcetype": "test:indextime:sourcetype:modinput_host_event_time_plugin", '
            '"source": "pytest-splunk-addon:modinput", '
            '"event": "test_modinput_2 host=modinput_host_event_time_plugin.samples_2", '
            '"index": "main", '
            '"host": "modinput_host_event_time_plugin.samples_2"'
            "}, {"
            '"sourcetype": "pytest_splunk_addon", '
            '"source": "pytest_splunk_addon:hec:event", '
            '"event": "fake event nothing happened", '
            '"index": "fake_index", '
            '"host": "fake host", '
            '"time": 1234.5678'
            "}]",
        )
    ]


@pytest.fixture()
def file_monitor_events():
    return [
        SampleEvent(
            event="host=test-host-file_monitor_host_prefix.sample-2 Test for host_prefix file_monitor"
            "host=test-host-file_monitor_host_prefix.sample-4 Test for host_prefix file_monitor",
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
            event="test_failing_1 src=10.1.0.81 dest_ip=10.100.0.91 src_port=4889 dest_port=21 "
            "dvc=172.16.22.73 user=user297 test_list_all=a test_email=user297@email.com",
            metadata={
                "sourcetype": "test:indextime:failing",
                "host_type": "plugin",
                "input_type": "file_monitor",
                "source": "pytest-splunk-addon:file_monitor",
                "sourcetype_to_search": "test:indextime:failing",
                "sample_count": "1",
                "earliest": "-60m",
                "timestamp_type": "event",
                "host": "failing-samples-1",
                "id": "failing.samples_1",
                "expected_event_count": 2,
            },
            sample_name="failing.samples",
        ),
        SampleEvent(
            event="fake event nothing happened src=0.0.0.0 src_port=5050 dest=10.0.0.1 dest_port=6060",
            metadata={
                "input_type": "file_monitor",
                "index": "fake_index",
            },
            sample_name="fake.samples",
        ),
    ]


@pytest.fixture()
def file_monitor_posts_sent():
    return [
        (
            f"POST {HEC_URI}/raw?"
            "sourcetype=test:indextime:file_monitor_host_prefix&"
            "source=pytest-splunk-addon:file_monitor&"
            "index=main&"
            "host=file_monitor_host_prefix.sample",
            "host=test-host-file_monitor_host_prefix.sample-2 Test for host_prefix file_monitor"
            "host=test-host-file_monitor_host_prefix.sample-4 Test for host_prefix file_monitor",
        ),
        (
            f"POST {HEC_URI}/raw?"
            "sourcetype=test:indextime:failing&"
            "source=pytest-splunk-addon:file_monitor&"
            "index=main&"
            "host=failing-samples-1",
            "test_failing_1 src=10.1.0.81 dest_ip=10.100.0.91 src_port=4889 dest_port=21 "
            "dvc=172.16.22.73 user=user297 test_list_all=a test_email=user297@email.com",
        ),
        (
            f"POST {HEC_URI}/raw?"
            "sourcetype=pytest_splunk_addon&"
            "source=pytest_splunk_addon:hec:raw&"
            "index=fake_index",
            "fake event nothing happened src=0.0.0.0 src_port=5050 dest=10.0.0.1 dest_port=6060",
        ),
    ]


@pytest.fixture()
def metric_events():
    return [
        {
            "event": "fake metric event sample 1 src=0.0.0.0 dest=10.0.0.1",
            "source": "pytest-splunk-addon:metric",
            "sourcetype": "test:metric:file_monitor_host_prefix",
            "input_type": "metric",
            "host_type": "event",
            "index": "fake_index",
            "host": "file_monitor_host_prefix.sample",
            "sample_name": "fake_metric_host_prefix.sample_1",
        },
        # SampleEvent(
        #     event="fake metric event sample 2 src=127.0.0.1 dest=10.0.0.2",
        #     metadata={
        #         "source": "pytest-splunk-addon:metric",
        #         "sourcetype": "test:metric:file_monitor_host_prefix",
        #         "input_type": "metric",
        #         "host_type": "event",
        #         "host": "file_monitor_host_prefix.sample",
        #     },
        #     sample_name="fake_metric_host_prefix.sample_1",
        # ),
    ]


@pytest.fixture()
def metric_posts_sent():
    return [
        (
            f"POST {HEC_URI}",
            "[{"
            '"event": "fake metric event sample 1 src=0.0.0.0 dest=10.0.0.1", '
            '"source": "pytest-splunk-addon:metric", '
            '"sourcetype": "test:metric:file_monitor_host_prefix", '
            '"input_type": "metric", '
            '"host_type": "event", '
            '"index": "fake_index", '
            '"host": "file_monitor_host_prefix.sample", '
            '"sample_name": "fake_metric_host_prefix.sample_1"'
            "}]",
        )
    ]


@pytest.fixture()
def tokenized_events(file_monitor_events, modinput_events):
    te = []
    te.extend(file_monitor_events)
    te.extend(modinput_events)
    return te


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
