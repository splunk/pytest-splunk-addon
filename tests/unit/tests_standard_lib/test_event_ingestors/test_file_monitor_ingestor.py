import pytest
from unittest.mock import patch, call
from urllib.parse import unquote
from requests.exceptions import ConnectionError
from collections import namedtuple
from os import sep as os_sep
from pytest_splunk_addon.event_ingestors.file_monitor_ingestor import (
    FileMonitorEventIngestor,
)

file_name = "pytest_splunk_addon.event_ingestors.file_monitor_ingestor"
required_config = {
    "uf_host": "localhost",
    "uf_port": "8888",
    "uf_username": "admin",
    "uf_password": "secret",
}
sample_event = namedtuple("SampleEvent", ["event", "metadata"], defaults=[None, None])


def test_ingest(mock_object):
    mock_object(f"{file_name}.sleep")
    events = ["event_1", "event_2", "event_3"]
    with patch.object(
        FileMonitorEventIngestor, "create_output_conf"
    ) as create_output_conf_mock, patch.object(
        FileMonitorEventIngestor, "create_event_file"
    ) as create_event_file_mock, patch.object(
        FileMonitorEventIngestor, "create_inputs_stanza"
    ) as create_inputs_stanza_mock:
        fmei = FileMonitorEventIngestor(required_config)
        fmei.ingest(events, 20)
        create_output_conf_mock.assert_called_once_with()
        create_event_file_mock.assert_has_calls([call(event) for event in events])
        create_inputs_stanza_mock.assert_has_calls([call(event) for event in events])
        assert (
            create_event_file_mock.call_count
            == create_inputs_stanza_mock.call_count
            == len(events)
        )


def test_create_output_conf(requests_mock):
    requests_mock.post("https://localhost:8888/services/data/outputs/tcp/group")
    fmei = FileMonitorEventIngestor(required_config)
    fmei.create_output_conf()
    sent_requests = [
        (unquote(str(req)), unquote(req.text)) for req in requests_mock.request_history
    ]
    assert sent_requests == [
        (
            "POST https://localhost:8888/services/data/outputs/tcp/group",
            "name=uf_monitor&servers=splunk:9997",
        )
    ]


@pytest.mark.parametrize(
    "response, message",
    [
        (
            {"text": "Not Found", "status_code": 404},
            "Unable to create stanza in outputs.conf\nStatus code: 404 \nReason: None \ntext:Not Found",
        ),
        (
            {"exc": ConnectionError("test connection error")},
            "Unable to connect to Universal forwarder, test connection error",
        ),
    ],
)
def test_create_output_conf_bad_request(requests_mock, caplog, response, message):
    requests_mock.post(
        "https://localhost:8888/services/data/outputs/tcp/group", **response
    )
    fmei = FileMonitorEventIngestor(required_config)
    fmei.create_output_conf()
    assert message in caplog.messages


def test_create_event_file(open_mock):
    with patch.object(
        FileMonitorEventIngestor, "get_file_path", return_value="fake_file"
    ):
        fmei = FileMonitorEventIngestor(required_config)
        fmei.create_event_file(
            sample_event(
                event="CREATE EVENT",
                metadata={"host": "localhost", "source": "sys.log"},
            )
        )
        open_mock.assert_has_calls(
            [
                call("fake_file", "w+"),
                call().__enter__(),
                call().write("CREATE EVENT"),
                call().__exit__(None, None, None),
            ]
        )


def test_create_event_file_gets_an_exception(open_mock, caplog):
    open_mock().write.side_effect = Exception("test error")
    with patch.object(
        FileMonitorEventIngestor, "get_file_path", return_value="fake_file"
    ):
        fmei = FileMonitorEventIngestor(required_config)
        fmei.create_event_file(
            sample_event(
                event="CREATE EVENT",
                metadata={"host": "localhost", "source": "sys.log"},
            )
        )
        assert (
            "Unable to create event file for host : localhost, Reason : test error"
            in caplog.messages
        )


@pytest.mark.parametrize(
    "event, post_args",
    [
        (
            sample_event(
                metadata={"sourcetype": "splunkd", "index": "ut", "host_type": "plugin"}
            ),
            f"name={os_sep}home{os_sep}uf_files{os_sep}host_name{os_sep}sample_name&"
            f"sourcetype=splunkd&index=ut&disabled=False&crc-salt=<SOURCE>&host_segment=3",
        ),
        (
            sample_event(metadata={"host_type": "modinput"}),
            f"name={os_sep}home{os_sep}uf_files{os_sep}host_name{os_sep}sample_name&"
            f"sourcetype=pytest_splunk_addon&index=main&disabled=False&crc-salt=<SOURCE>",
        ),
    ],
)
def test_create_inputs_stanza(requests_mock, event, post_args):
    requests_mock.post(
        "https://localhost:8888/servicesNS/nobody/search/data/inputs/monitor"
    )
    with patch.object(
        FileMonitorEventIngestor,
        "get_file_path",
        return_value=f"{os_sep}home{os_sep}uf_files{os_sep}host_name{os_sep}sample_name",
    ):
        fmei = FileMonitorEventIngestor(required_config)
        fmei.create_inputs_stanza(event)
        sent_requests = [
            (unquote(str(req)), unquote(req.text))
            for req in requests_mock.request_history
        ]
        assert sent_requests == [
            (
                "POST https://localhost:8888/servicesNS/nobody/search/data/inputs/monitor",
                post_args,
            )
        ]


@pytest.mark.parametrize(
    "response, message",
    [
        (
            {"text": "Not Found", "status_code": 404},
            f"Unable to add stanza in inputs.conf for Path : {os_sep}home{os_sep}uf_files{os_sep}host_name{os_sep}"
            f"sample_name \nStatus code: 404 \nReason: None \ntext:Not Found",
        ),
        (
            {"exc": ConnectionError("test connection error")},
            "Unable to connect to Universal forwarder, test connection error",
        ),
    ],
)
def test_create_inputs_stanza_bad_request(requests_mock, caplog, response, message):
    requests_mock.post(
        "https://localhost:8888/servicesNS/nobody/search/data/inputs/monitor",
        **response,
    )
    with patch.object(
        FileMonitorEventIngestor,
        "get_file_path",
        return_value=f"{os_sep}home{os_sep}uf_files{os_sep}host_name{os_sep}sample_name",
    ):
        fmei = FileMonitorEventIngestor(required_config)
        fmei.create_inputs_stanza(sample_event(metadata={"host_type": "modinput"}))
        assert message in caplog.messages


def test_get_file_path(open_mock, mock_object, os_path_join_file_mock):
    os_getcwd_mock = mock_object("os.getcwd")
    os_getcwd_mock.return_value = "/fake_path"
    os_path_exists = mock_object("os.path.exists")
    os_path_exists.return_value = False
    os_mkdir = mock_object("os.mkdir")
    fmei = FileMonitorEventIngestor(required_config)
    out = fmei.get_file_path(
        sample_event(metadata={"host": "localhost", "source": "sys.log"})
    )
    assert out == "/fake_path/uf_files/localhost/sys.log"
    os_mkdir.assert_called_once_with("/fake_path/uf_files/localhost")
