import pytest
from unittest.mock import patch, call
from collections import namedtuple
from copy import deepcopy
from pytest_splunk_addon.standard_lib.index_tests.test_generator import (
    IndexTimeTestGenerator,
)

module = "pytest_splunk_addon.standard_lib.index_tests.test_generator"
sample_event = namedtuple(
    "SampleEvent",
    ["metadata", "key_fields", "sample_name", "time_values"],
    defaults=[{}, {}, "", [1]],
)


def patch_object(func_to_mock, **kwargs):
    return patch.object(IndexTimeTestGenerator, func_to_mock, **kwargs)


def test_generate_tests_without_conf_file(mock_object, caplog):
    sample_generator_mock = mock_object(f"{module}.SampleXdistGenerator")
    sample_generator_mock.return_value = sample_generator_mock
    sample_generator_mock.get_samples.return_value = {"tokenized_events": []}
    list(
        IndexTimeTestGenerator().generate_tests(
            True, "fake_app_path", "fake_config_path", "key_fields"
        )
    )
    assert caplog.messages == [
        "Index time tests cannot be executed without pytest-splunk-addon-data.conf"
    ]


@pytest.mark.parametrize(
    "test_type, tokenized_events, expected_output",
    [
        (
            "key_fields",
            [
                sample_event(
                    metadata={
                        "identifier": "sample.1",
                        "host": ["localhost", "remotehost"],
                        "host_prefix": "p_",
                    },
                    key_fields={"host": "localhost"},
                )
            ],
            [
                (
                    sample_event(
                        metadata={
                            "identifier": "sample.1",
                            "host": ["localhost", "remotehost"],
                            "host_prefix": "p_",
                        },
                        key_fields={"host": ["p_localhost"]},
                    ),
                    "sample.1",
                    ["localhost", "remotehost"],
                )
            ],
        ),
        (
            "_time",
            [
                sample_event(
                    metadata={
                        "identifier": "sample.2",
                        "host": "localhost",
                        "timestamp_type": "event",
                    },
                )
            ],
            [
                (
                    sample_event(
                        metadata={
                            "identifier": "sample.2",
                            "host": "localhost",
                            "timestamp_type": "event",
                        },
                    ),
                    "sample.2",
                    ["localhost"],
                )
            ],
        ),
        (
            "_time",
            [
                sample_event(
                    metadata={
                        "identifier": "sample.2",
                        "host": "localhost",
                        "timestamp_type": "event",
                    },
                    time_values=[],
                )
            ],
            [],
        ),
    ],
)
def test_generate_tests_triggers_generate_params(
    mock_object,
    test_type,
    tokenized_events,
    expected_output,
):
    sample_generator_mock = mock_object(f"{module}.SampleXdistGenerator")
    sample_generator_mock.return_value = sample_generator_mock
    sample_event_mock = mock_object(f"{module}.SampleEvent")
    sample_event_mock.copy.side_effect = lambda x: deepcopy(x)
    sample_generator_mock.get_samples.return_value = {
        "tokenized_events": tokenized_events,
        "conf_name": "psa-data-gen",
    }
    with patch_object(
        "get_hosts",
        side_effect=lambda event: event.metadata["host"]
        if type(event.metadata["host"]) == list
        else [event.metadata["host"]],
    ), patch_object(
        "add_host_prefix",
        side_effect=lambda host_prefix, hosts: [
            host_prefix + str(host) for host in hosts
        ]
        if type(hosts) == list
        else [host_prefix + str(hosts)],
    ), patch_object(
        "generate_params",
        side_effect=lambda event, ids, hosts: ((event, ids, hosts) for x in range(1)),
    ) as generate_params_mock:
        out = list(
            IndexTimeTestGenerator().generate_tests(
                True, "fake_app_path", "fake_config_path", test_type
            )
        )
        assert out == expected_output
        generate_params_mock.assert_has_calls([call(*args) for args in expected_output])
        assert generate_params_mock.call_count == len(expected_output)


def test_generate_tests_triggers_generate_line_breaker_tests(mock_object):
    sample_generator_mock = mock_object(f"{module}.SampleXdistGenerator")
    sample_generator_mock.return_value = sample_generator_mock
    sample_generator_mock.get_samples.return_value = {
        "tokenized_events": [sample_event(sample_name="line_breaker_event")],
        "conf_name": "psa-data-gen",
    }
    with patch_object(
        "generate_line_breaker_tests",
        side_effect=lambda events: (event for event in events),
    ) as generate_line_breaker_tests:
        out = list(
            IndexTimeTestGenerator().generate_tests(
                True, "fake_app_path", "fake_config_path", "line_breaker"
            )
        )
        assert out == [sample_event(sample_name="line_breaker_event")]
        generate_line_breaker_tests.assert_called_once_with(
            [sample_event(sample_name="line_breaker_event")]
        )


def test_generate_line_breaker_tests(mock_object):
    mock_object(f"{module}.raise_warning")
    tokenized_events = [
        sample_event(
            metadata={
                "sample_count": 5,
                "expected_event_count": 3,
                "sourcetype": "splunkd",
                "input_type": "file_monitor",
                "host": ["host1", "host2"],
            },
            sample_name="sample.1",
        ),
        sample_event(
            metadata={
                "sample_count": 5,
                "expected_event_count": "three",
                "sourcetype": "splunkd",
                "input_type": "modinput",
                "host": "host1",
            },
            sample_name="sample.2",
        ),
        sample_event(
            metadata={
                "sample_count": 1,
                "expected_event_count": 1,
                "sourcetype": "sc4s",
                "input_type": "syslog_tcp",
                "host": ["host2", "host3"],
            },
            sample_name="sample.1",
        ),
    ]
    with patch_object(
        "get_sourcetype",
        side_effect=lambda event: event.metadata["sourcetype"],
    ), patch_object(
        "get_hosts",
        side_effect=lambda event: event.metadata["host"]
        if type(event.metadata["host"]) == list
        else [event.metadata["host"]],
    ), patch.object(
        pytest, "param", side_effect=lambda x, id: (x, id)
    ) as param_mock:
        out = list(
            IndexTimeTestGenerator().generate_line_breaker_tests(tokenized_events)
        )
        assert out == [
            (
                {
                    "sourcetype": "splunkd",
                    "expected_event_count": 15,
                    "host": {"host1", "host2", "host3"},
                },
                "splunkd::sample.1",
            ),
            (
                {
                    "sourcetype": "splunkd",
                    "expected_event_count": 15,
                    "host": {"host1"},
                },
                "splunkd::sample.2",
            ),
        ]
        param_mock.assert_has_calls(
            [
                call(
                    {
                        "sourcetype": "splunkd",
                        "expected_event_count": 15,
                        "host": {"host1", "host2", "host3"},
                    },
                    id="splunkd::sample.1",
                ),
                call(
                    {
                        "sourcetype": "splunkd",
                        "expected_event_count": 15,
                        "host": {"host1"},
                    },
                    id="splunkd::sample.2",
                ),
            ]
        )


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
    with patch_object(
        "add_host_prefix",
        side_effect=lambda host_prefix, hosts: [
            host_prefix + str(host) for host in hosts
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


@pytest.mark.parametrize(
    "identifier_key, hosts, expected_output",
    [
        (["identifier_1", "identifier_2"], [], ["identifier_1", "identifier_2"]),
        ([], ["host1", "host2"], ["host1", "host2"]),
    ],
)
def test_generate_params(identifier_key, hosts, expected_output):
    with patch_object(
        "generate_identifier_params",
        side_effect=lambda event, ids: (id for id in ids),
    ) as generate_identifier_params_mock, patch_object(
        "generate_hosts_params",
        side_effect=lambda event, hosts: (host for host in hosts),
    ) as generate_hosts_params_mock:
        out = list(
            IndexTimeTestGenerator().generate_params(
                "empty_event", identifier_key, hosts
            )
        )
        assert out == expected_output
        generate_identifier_params_mock.assert_has_calls(
            [call("empty_event", identifier_key)] if identifier_key else []
        )
        generate_hosts_params_mock.assert_has_calls(
            [call("empty_event", hosts)] if hosts else []
        )


@pytest.mark.parametrize(
    "tokenized_event, expected_output",
    [
        (
            sample_event(
                key_fields={"key1": ["val1a", "val1b"], "key2": ["val2a", "val2b"]}
            ),
            [
                (
                    {
                        "identifier": "key1=val1a",
                        "sourcetype": "splunkd",
                        "source": "utility.log",
                        "tokenized_event": sample_event(
                            key_fields={
                                "key1": ["val1a", "val1b"],
                                "key2": ["val2a", "val2b"],
                            }
                        ),
                    },
                    "splunkd::key1:val1a",
                ),
                (
                    {
                        "identifier": "key1=val1b",
                        "sourcetype": "splunkd",
                        "source": "utility.log",
                        "tokenized_event": sample_event(
                            key_fields={
                                "key1": ["val1a", "val1b"],
                                "key2": ["val2a", "val2b"],
                            }
                        ),
                    },
                    "splunkd::key1:val1b",
                ),
            ],
        )
    ],
)
def test_generate_identifier_params(tokenized_event, expected_output):
    with patch_object("get_sourcetype", return_value="splunkd"), patch_object(
        "get_source", return_value="utility.log"
    ), patch.object(pytest, "param", side_effect=lambda x, id: (x, id)) as param_mock:
        out = list(
            IndexTimeTestGenerator().generate_identifier_params(tokenized_event, "key1")
        )
        assert out == expected_output
        param_mock.assert_has_calls(
            [call(arg[0], id=arg[1]) for arg in expected_output]
        )
        assert param_mock.call_count == len(expected_output)


@pytest.mark.parametrize(
    "hosts, expected_output",
    [
        (
            ["localhost"],
            (
                {
                    "hosts": ["localhost"],
                    "sourcetype": "splunkd",
                    "source": "utility.log",
                    "tokenized_event": sample_event(sample_name="empty_event"),
                },
                "splunkd::localhost",
            ),
        ),
        (
            ["host1", "host2", "host3"],
            (
                {
                    "hosts": ["host1", "host2", "host3"],
                    "sourcetype": "splunkd",
                    "source": "utility.log",
                    "tokenized_event": sample_event(sample_name="empty_event"),
                },
                "splunkd::host1_to_host3",
            ),
        ),
        (
            [],
            (
                {
                    "hosts": [],
                    "sourcetype": "splunkd",
                    "source": "utility.log",
                    "tokenized_event": sample_event(sample_name="empty_event"),
                },
                "splunkd::empty_event",
            ),
        ),
    ],
)
def test_generate_hosts_params(hosts, expected_output):
    with patch_object("get_sourcetype", return_value="splunkd"), patch_object(
        "get_source", return_value="utility.log"
    ), patch.object(pytest, "param", side_effect=lambda x, id: (x, id)) as param_mock:
        out = list(
            IndexTimeTestGenerator().generate_hosts_params(
                sample_event(sample_name="empty_event"), hosts
            )
        )
        assert out == [expected_output]
        param_mock.assert_called_once_with(expected_output[0], id=expected_output[1])
