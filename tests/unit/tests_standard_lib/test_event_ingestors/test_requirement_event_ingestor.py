from dataclasses import dataclass
from unittest.mock import MagicMock, call, patch

import pytest

from pytest_splunk_addon.standard_lib.event_ingestors.requirement_event_ingester import (
    ET,
    RequirementEventIngestor,
)

module = "pytest_splunk_addon.standard_lib.event_ingestors.requirement_event_ingester"


@dataclass()
class SampleEvent:
    event: str
    metadata: dict
    sample_name: str
    key_fields: dict = None
    time_values: list = None


@pytest.fixture()
def sample_event_mock(monkeypatch):
    monkeypatch.setattr(f"{module}.SampleEvent", SampleEvent)


@pytest.fixture()
def get_root_mocked(monkeypatch):
    tree_mock = MagicMock()
    tree_mock.return_value = tree_mock
    tree_mock.getroot.return_value = "root"
    monkeypatch.setattr(f"{module}.ET.parse", tree_mock)


@pytest.fixture()
def root_mock():
    root_mock, raw_mock = MagicMock(), MagicMock()
    root_mock.return_value = root_mock
    raw_mock.return_value = raw_mock
    raw_mock.text = "raw event extracted"
    root_mock.iter.return_value = [raw_mock]
    return root_mock


@pytest.fixture()
def configparser_mock(monkeypatch):
    config_mock = MagicMock()
    config_mock.sections.return_value = [
        "ta_fiction_lookup",
        "fiction-rsc-delim-fields",
        "fiction-tsc-regex",
    ]
    items = {
        "ta_fiction_lookup": {"a": 1, "b": 3},
        "fiction-rsc-delim-fields": {
            "dest_key": "MetaData:Sourcetype",
            "fields": "day_id, event_id, end_time, start_time",
            "format": 'comp::"$1"',
        },
        "fiction-tsc-regex": {
            "dest_key": "MetaData:Sourcetype",
            "regex": "group=(?<extractone>[^,]+)",
        },
    }
    config_mock.__getitem__.side_effect = lambda key: items[key]
    config_mock.return_value = config_mock
    monkeypatch.setattr(
        "configparser.ConfigParser",
        config_mock,
    )


@pytest.fixture()
def requirement_ingestor_mocked(monkeypatch, mock_object):
    mock_object(
        f"{module}.RequirementEventIngestor.check_xml_format", return_value=True
    )
    mock_object(
        f"{module}.RequirementEventIngestor.get_models", return_value="Network_Traffic"
    )
    mock_object(
        f"{module}.RequirementEventIngestor.extract_transport_tag",
        return_value="syslog",
    )
    root_mock = mock_object(f"{module}.RequirementEventIngestor.get_root")
    root_mock.return_value = root_mock
    root_mock.iter.return_value = ["session created", "session closed"]
    ere_mock = mock_object(
        f"{module}.RequirementEventIngestor.extract_raw_events",
        side_effect=lambda x: f"event: {x}",
    )
    return {"root_mock": root_mock, "ere_mock": ere_mock}


def test_check_xml_format():
    with patch.object(ET, "parse", lambda x: x):
        req = RequirementEventIngestor("fake_path")
        assert req.check_xml_format("fake_file") is True
        assert req.check_xml_format("") is False


def test_root_can_be_obtained(get_root_mocked):
    req = RequirementEventIngestor("fake_path")
    assert req.get_root("fake_file_name") == "root"


def test_raw_events_can_be_extracted(root_mock):
    req = RequirementEventIngestor("fake_path")
    assert req.extract_raw_events(root_mock) == "raw event extracted"


def test_events_can_be_obtained(
    mock_object, requirement_ingestor_mocked, sample_event_mock
):
    mock_object("os.path.isdir", return_value=True)
    mock_object("os.listdir", return_value=["sample.log"])
    req = RequirementEventIngestor("fake_path")
    assert req.get_events() == [
        SampleEvent(
            event="event: session created",
            metadata={
                "input_type": "syslog_tcp",
                "index": "main",
                "source": "",
                "host": "",
                "sourcetype": "",
                "timestamp_type": "event",
                "host_type": None,
            },
            sample_name="requirement_test",
        ),
        SampleEvent(
            event="event: session closed",
            metadata={
                "input_type": "syslog_tcp",
                "index": "main",
                "source": "",
                "host": "",
                "sourcetype": "",
                "timestamp_type": "event",
                "host_type": None,
            },
            sample_name="requirement_test",
        ),
    ]
    requirement_ingestor_mocked["root_mock"].iter.assert_has_calls([call("event")])
    requirement_ingestor_mocked["ere_mock"].assert_has_calls(
        [call("session created"), call("session closed")]
    )
