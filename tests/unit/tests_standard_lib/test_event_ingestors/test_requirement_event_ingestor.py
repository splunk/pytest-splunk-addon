import pytest
from unittest.mock import MagicMock, call, patch
from recordtype import recordtype
from pytest_splunk_addon.standard_lib.event_ingestors.requirement_event_ingester import (
    RequirementEventIngestor,
    SrcRegex,
    ET,
)


module = "pytest_splunk_addon.standard_lib.event_ingestors.requirement_event_ingester"
src_regex = recordtype("SrcRegex", [("regex_src", None), ("source_type", None)])
sample_event = recordtype(
    "SampleEvent",
    ["event", "metadata", "sample_name", ("key_fields", None), ("time_values", None)],
)


@pytest.fixture()
def sample_event_mock(monkeypatch):
    monkeypatch.setattr(f"{module}.SampleEvent", sample_event)


@pytest.fixture()
def src_regex_mock(monkeypatch):
    monkeypatch.setattr(f"{module}.SrcRegex", src_regex)


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
        f"{module}.RequirementEventIngestor.extract_regex_transforms",
        return_value=[src_regex("event", "host::$1")],
    )
    mock_object(
        f"{module}.RequirementEventIngestor.check_xml_format", return_value=True
    )
    root_mock = mock_object(f"{module}.RequirementEventIngestor.get_root")
    root_mock.return_value = root_mock
    root_mock.iter.return_value = ["session created", "session closed"]
    ere_mock = mock_object(
        f"{module}.RequirementEventIngestor.extract_raw_events",
        side_effect=lambda x: f"event: {x}",
    )
    es_mock = mock_object(
        f"{module}.RequirementEventIngestor.extract_sourcetype",
        side_effect=("host$1", "host$2"),
    )
    return {"root_mock": root_mock, "ere_mock": ere_mock, "es_mock": es_mock}


def test_src_regex_can_be_instantiated():
    srcregex = SrcRegex()
    assert hasattr(srcregex, "regex_src")
    assert hasattr(srcregex, "source_type")


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


def test_regex_transforms_can_be_extracted(
    open_mock, configparser_mock, src_regex_mock
):
    req = RequirementEventIngestor("fake_path")
    assert req.extract_regex_transforms() == [
        src_regex(None, 'comp::"$1"'),
        src_regex("group=(?<extractone>[^,]+)", None),
    ]


def test_sourcetype_can_be_extracted():
    req = RequirementEventIngestor("fake_path")
    assert (
        req.extract_sourcetype(
            [
                src_regex("alert", "source::host$1"),
                src_regex("emergency", "source::host$2"),
            ],
            "event: alert something happened",
        )
        == "host$1"
    )


def test_events_can_be_obtained(
    mock_object, requirement_ingestor_mocked, sample_event_mock
):
    mock_object("os.path.isdir", return_value=True)
    mock_object("os.listdir", return_value=["sample.log"])
    req = RequirementEventIngestor("fake_path")
    assert req.get_events() == [
        sample_event(
            event="event: session created",
            metadata={"input_type": "default", "sourcetype": "host$1", "index": "main"},
            sample_name="requirement_test",
        ),
        sample_event(
            event="event: session closed",
            metadata={"input_type": "default", "sourcetype": "host$2", "index": "main"},
            sample_name="requirement_test",
        ),
    ]
    requirement_ingestor_mocked["root_mock"].iter.assert_has_calls([call("event")])
    requirement_ingestor_mocked["ere_mock"].assert_has_calls(
        [call("session created"), call("session closed")]
    )
    requirement_ingestor_mocked["es_mock"].assert_has_calls(
        [
            call([src_regex("event", "host::$1")], "event: session created"),
            call([src_regex("event", "host::$1")], "event: session closed"),
        ]
    )
