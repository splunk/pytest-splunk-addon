import pytest
from unittest.mock import patch
from pytest_splunk_addon.standard_lib.event_ingestors.hec_raw_ingestor import HECRawEventIngestor
from urllib.parse import unquote


HEC_URI = 'https://127.0.0.1:55238/services/collector'


@pytest.fixture()
def raw_ingestor(requests_mock):
    return HECRawEventIngestor({
        'session_headers': {
            'Authorization': 'Splunk 9b741d03-43e9-4164-908b-e09102327d22'
        },
        'splunk_hec_uri': HEC_URI})


def test_events_can_be_ingested(requests_mock, raw_ingestor, file_monitor_events):
    requests_mock.post(f'{HEC_URI}/raw')
    raw_ingestor.ingest(file_monitor_events, 1)
    assert requests_mock.call_count == 2
    sent_requests = [(unquote(str(req)), req.text) for req in requests_mock.request_history]
    req1 = (
        f'POST {HEC_URI}/raw?' \
         'sourcetype=test:indextime:file_monitor_host_prefix&' \
         'source=pytest-splunk-addon:file_monitor&' \
         'index=main&' \
         'host=file_monitor_host_prefix.sample',
         "host=test-host-file_monitor_host_prefix.sample-2 Test for host_prefix file_monitor"
         "host=test-host-file_monitor_host_prefix.sample-4 Test for host_prefix file_monitor"
            )
    req2 = (
        f'POST {HEC_URI}/raw?' \
         'sourcetype=test:indextime:failing&' \
         'source=pytest-splunk-addon:file_monitor&' \
         'index=main&' \
         'host=failing-samples-1',
         'test_failing_1 src=10.1.0.81 dest_ip=10.100.0.91 src_port=4889 dest_port=21 '
         'dvc=172.16.22.73 user=user297 test_list_all=a test_email=user297@email.com')
    assert set([req1, req2]) == set(sent_requests)
