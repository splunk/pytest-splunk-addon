import pytest
from unittest.mock import MagicMock, patch
from collections import namedtuple
from pytest_splunk_addon.standard_lib.index_tests.test_generator import (
    IndexTimeTestGenerator,
)

sample_event = namedtuple(
    "SampleEvent", ["metadata", "key_fields", "sample_name"], defaults=[{}, {}, ""]
)


@pytest.fixture()
def sample_generator_mock(monkeypatch):
    sg = MagicMock()
    monkeypatch.setattr(
        "pytest_splunk_addon.standard_lib.index_tests.test_generator.SampleXdistGenerator",
        sg,
    )
    return sg


def test_generate_tests_without_conf_file(sample_generator_mock, caplog):
    sample_generator_mock.return_value = sample_generator_mock
    sample_generator_mock.get_samples.return_value = {"tokenized_events": []}
    list(
        IndexTimeTestGenerator().generate_tests(
            True, "fake_app_path", "fake_config_path", "key_fields"
        )
    )
    assert caplog.messages == [
        "Index Time tests cannot be executed using eventgen.conf, pytest-splunk-addon-data.conf is required."
    ]


def test_generate_tests(sample_generator_mock):
    sample_generator_mock.return_value = sample_generator_mock
    sample_generator_mock.get_samples.return_value = {"tokenized_events": []}
    pass


@pytest.mark.parametrize(
    "event, expected_output, log",
    [
        (
            sample_event(
                metadata={
                    "host_type": "plugin",
                    "host": ["host1", "host2"],
                    "host_prefix": "p_",
                },
                sample_name="sample.1",
            ),
            ["p_host1", "p_host2"],
            ["Returning host with value ['p_host1', 'p_host2'] for stanza sample.1"],
        ),
        (
            sample_event(
                metadata={"host": "host", "host_prefix": "p_"}, sample_name="sample.2"
            ),
            ["p_host"],
            ["Returning host with value ['p_host'] for stanza sample.2"],
        ),
        (
            sample_event(
                metadata={"host_type": "event", "host": "host", "host_prefix": "p_"},
                key_fields={"host": "key_host"},
                sample_name="sample.3",
            ),
            ["p_key_host"],
            ["Returning host with value ['p_key_host'] for stanza sample.3"],
        ),
        (
            sample_event(
                metadata={"host_type": "other_host", "host": "host"},
                key_fields={"host": "key_host"},
                sample_name="sample.4",
            ),
            None,
            [
                "Invalid 'host_type' for stanza sample.4",
                "Returning host with value None for stanza sample.4",
            ],
        ),
    ],
)
def test_get_hosts(event, expected_output, log, caplog):
    with patch.object(
        IndexTimeTestGenerator,
        "add_host_prefix",
        side_effect=lambda host_prefix, hosts: [
            host_prefix + str(host) for host in hosts if hosts
        ],
    ):
        assert IndexTimeTestGenerator().get_hosts(event) == expected_output
        assert caplog.messages == log


def test_add_host_prefix():
    assert IndexTimeTestGenerator().add_host_prefix(
        "prefix_", ["host1", "host2", "host3"]
    ) == ["prefix_host1", "prefix_host2", "prefix_host3"]


@pytest.mark.parametrize(
    "event, expected_output",
    [
        (sample_event(metadata={}), "*"),
        (
            sample_event(
                metadata={"sourcetype_to_search": "splunk1", "sourcetype": "splunk2"}
            ),
            "splunk1",
        ),
        (sample_event(metadata={"sourcetype": "splunk2"}), "splunk2"),
    ],
)
def test_get_sourcetype(event, expected_output):
    assert IndexTimeTestGenerator().get_sourcetype(event) == expected_output


@pytest.mark.parametrize(
    "event, expected_output",
    [
        (sample_event(metadata={}), "*"),
        (
            sample_event(metadata={"source_to_search": "splunk1", "source": "splunk2"}),
            "splunk1",
        ),
        (sample_event(metadata={"source": "splunk2"}), "splunk2"),
    ],
)
def test_get_source(event, expected_output):
    assert IndexTimeTestGenerator().get_source(event) == expected_output
