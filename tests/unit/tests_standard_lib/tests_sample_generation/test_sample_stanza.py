import os
import pytest
from collections import namedtuple
from unittest.mock import MagicMock, patch, mock_open

from pytest_splunk_addon.standard_lib.sample_generation.sample_stanza import (
    SampleStanza,
)

HOST = "path_to.file"
SAMPLE_PATH = f"/sample/{HOST}"
tokens = {
    "token_1": {"replacementType": "all"},
    "token_2": {"replacementType": "random"},
}
rule_obj = namedtuple("rule_obj", ["metadata", "update_requirement_test_field"])


def get_params_for_get_raw_sample():
    result = []
    for input_type in "modinput", "windows_input":
        result.append(
            (
                {
                    "tokens": tokens,
                    "input_type": input_type,
                },
                [
                    "sample_raw",
                    {"input_type": input_type, "host": "path_to.file_1"},
                    "path_to.file",
                ],
            )
        )
    for input_type in [
        "file_monitor",
        "scripted_input",
        "syslog_tcp",
        "syslog_udp",
        "default",
    ]:
        result.append(
            (
                {
                    "tokens": tokens,
                    "input_type": input_type,
                },
                [
                    "sample_raw",
                    {"input_type": input_type, "host": "path_to.file"},
                    "path_to.file",
                ],
            )
        )
    return result


class TestSampleStanza:
    @pytest.fixture
    def sample_stanza(self):
        def func(
            psa_data_params={"tokens": tokens},
            rule_mock_value="Test_rule",
            conf_name="sample_conf_name"
        ):
            with patch.object(os, "sep", "/"), patch(
                "pytest_splunk_addon.standard_lib.sample_generation.sample_stanza.Rule",
                MagicMock(return_value=rule_mock_value),
            ):
                ss = SampleStanza(SAMPLE_PATH, psa_data_params, conf_name)
            return ss

        return func

    def test_init(self, sample_stanza):
        ss = sample_stanza({"tokens": tokens})
        assert ss.sample_path == SAMPLE_PATH

    def test_get_raw_events(self, sample_stanza):
        ss = sample_stanza()
        ss._get_raw_sample = MagicMock(return_value="_get_raw_sample")
        ss.get_raw_events()
        assert ss.tokenized_events == "_get_raw_sample"

    def test_get_tokenized_events(self, sample_stanza):
        ss = sample_stanza()
        mock_1 = MagicMock()
        mock_2 = MagicMock()
        ss.tokenized_events = [mock_1, mock_2]
        with patch(
            "pytest_splunk_addon.standard_lib.sample_generation.sample_stanza.SampleEvent",
            MagicMock(),
        ) as sample_event_mock:
            sample_event_mock.update_metadata.return_value = ("one", "two", "three")
            assert list(ss.get_tokenized_events()) == [mock_1, mock_2]
            for m in mock_1, mock_2:
                assert m.event == "one"
                assert m.metadata == "two"
                assert m.key_fields == "three"

    @pytest.mark.parametrize(
        "psa_data_params, conf_name, expected",
        [
            (
                {"tokens": tokens},
                "something",
                [{"breaker": 1, "expected_event_count": 1}],
            ),
            (
                {"tokens": tokens, "count": "1"},
                "psa_data",
                [{"breaker": 1, "expected_event_count": 1}],
            ),
            (
                {"tokens": tokens, "expected_event_count": "1", "breaker": "4"},
                "som",
                [{"breaker": 1, "sample_count": 1}],
            ),
        ],
    )
    def test_tokenize(self, sample_stanza, psa_data_params, conf_name, expected):
        ss = sample_stanza(psa_data_params=psa_data_params, conf_name=conf_name)
        ss._get_raw_sample = MagicMock(return_value=[rule_obj({}, "")])
        rule = MagicMock()
        rule.apply.return_value = [
            rule_obj(
                {
                    "breaker": 1,
                },
                MagicMock(),
            )
        ]
        ss.sample_rules = [rule]
        ss.tokenize()
        assert [e.metadata for e in ss.tokenized_events] == expected

    def test_tokenize_empty_raw_event(self, sample_stanza):
        ss = sample_stanza()
        ss._get_raw_sample = MagicMock(return_value=[])
        rule = MagicMock()
        rule.apply.return_value = [rule_obj({"breaker": 1}, MagicMock())]
        ss.sample_rules = [rule]
        ss.tokenize()
        assert ss.tokenized_events == []

    @pytest.mark.parametrize(
        "rule_value, expected", [("value", ["value", "value"]), (None, [])]
    )
    def test_parse_rules(self, sample_stanza, rule_value, expected):
        ss = sample_stanza()
        ss._sort_tokens_by_replacement_type_all = MagicMock(
            return_value=[
                (1, {"replacement": "", "token": ""}),
                (3, {"replacement": "", "token": ""}),
            ]
        )
        with patch(
            "pytest_splunk_addon.standard_lib.sample_generation.sample_stanza.Rule",
            MagicMock(),
        ) as rule_mock:
            rule_mock.parse_rule.return_value = rule_value
            assert list(ss._parse_rules({"tokens": 2}, "sample_path")) == expected

    @pytest.mark.parametrize(
        "input_type, input_type_expected, messages, host",
        [
            ("tcp", "default", [], HOST),
            ("modinput", "modinput", [], HOST),
            (
                "syslog_tcp",
                "syslog_tcp",
                ["For input_type 'syslog_tcp', there should be no index set"],
                HOST,
            ),
            ("uf_file_monitor", "uf_file_monitor", [], "path-to-file"),
        ],
    )
    def test_parse_meta(
        self, caplog, sample_stanza, input_type, input_type_expected, messages, host
    ):
        ss = sample_stanza(
            {
                "host_type": "host",
                "timestamp_type": "tt",
                "timezone": "UTC",
                "sample_count": "11a",
                "expected_event_count": "hh",
                "count": "ll",
                "index": 1,
                "input_type": input_type,
                "tokens": {
                    "token_1": {"replacementType": "all"},
                    "token_2": {"replacementType": "random"},
                },
            }
        )
        assert ss.metadata == {
            "count": "100",
            "expected_event_count": "1",
            "host": host,
            "host_type": "plugin",
            "index": 1,
            "input_type": input_type_expected,
            "sample_count": "1",
            "timestamp_type": "plugin",
            "timezone": "0000",
        }

        assert all(message in caplog.messages for message in messages)

    def test_get_eventmetadata(self, sample_stanza):
        ss = sample_stanza()
        assert ss.host_count == 0
        assert ss.get_eventmetadata() == {
            "host": "path_to.file_1",
            "input_type": "default",
        }
        assert ss.host_count == 1

    @pytest.mark.parametrize(
        "sample_raw, expected",
        [
            ("aasampaale_raaw", ["aasamp", "aale_r", "aaw"]),
            ("sampaale_raaw", ["samp", "aale_r", "aaw"]),
        ],
    )
    def test_break_events(self, sample_stanza, sample_raw, expected):
        ss = sample_stanza(
            psa_data_params={
                "tokens": tokens,
                "breaker": "aa",
            }
        )
        assert ss.break_events(sample_raw) == expected

    @pytest.mark.parametrize(
        "psa_data_params, sample_event_params",
        [
            (
                {
                    "tokens": tokens,
                    "breaker": "aa",
                },
                [
                    "sample_raw",
                    {
                        "breaker": "aa",
                        "host": "path_to.file_1",
                        "input_type": "default",
                    },
                    "path_to.file",
                ],
            ),
            *get_params_for_get_raw_sample(),
        ],
    )
    def test_get_raw_sample(self, sample_stanza, psa_data_params, sample_event_params):
        ss = sample_stanza(psa_data_params=psa_data_params)
        data = "sample_raw"
        with patch("builtins.open", mock_open(read_data=data)), patch(
            "pytest_splunk_addon.standard_lib.sample_generation.sample_stanza.SampleEvent",
            MagicMock(return_value="sample_event"),
        ) as sample_event_mock:
            assert list(ss._get_raw_sample()) == ["sample_event"]
            sample_event_mock.assert_called_with(*sample_event_params)

    def test_get_raw_sample_empty_event(self, sample_stanza):
        ss = sample_stanza(
            psa_data_params={
                "tokens": tokens,
                "input_type": "file_monitor",
            }
        )
        data = ""
        with patch("builtins.open", mock_open(read_data=data)), patch(
            "pytest_splunk_addon.standard_lib.sample_generation.sample_stanza.SampleEvent",
            MagicMock(return_value="sample_event"),
        ) as sample_event_mock:
            assert list(ss._get_raw_sample()) == []
            sample_event_mock.assert_not_called()

    def test_break_events_exception(self, sample_stanza, caplog):
        ss = sample_stanza(
            psa_data_params={
                "tokens": {
                    "token_1": {"replacementType": "all"},
                    "token_2": {"replacementType": "random"},
                },
                "breaker": "aa",
            }
        )
        with patch("builtins.enumerate", MagicMock(side_effect=ValueError)):
            assert ss.break_events("aasampaale_raaw") == ["aasampaale_raaw"]
            assert "Invalid breaker for stanza path_to.file" in caplog.messages

    @pytest.mark.parametrize(
        "event, expected",
        [
            ({}, {}),
            ({"field": "field", "dummy": 1}, {}),
            (
                {
                    "cim": {
                        "models": {"model": "Alerts"},
                        "cim_fields": {
                            "field": [
                                {"@name": "dest", "@value": "192.168.0.1"},
                                {"@name": "signature_id", "@value": "405001"},
                                {"@name": "severity", "@value": "low"},
                                {"@name": "src", "@value": "192.168.0.1"},
                                {"@name": "type", "@value": "event"},
                            ]
                        },
                        "missing_recommended_fields": {
                            "field": ["app", "id", "user", "user_name"]
                        },
                    }
                },
                {
                    "cim_version": "latest",
                    "cim_fields": {
                        "dest": "192.168.0.1",
                        "severity": "low",
                        "signature_id": "405001",
                        "src": "192.168.0.1",
                        "type": "event",
                    },
                    "datamodels": {"model": "Alerts"},
                    "exceptions": {},
                    "missing_recommended_fields": ["app", "id", "user", "user_name"],
                },
            ),
            (
                {
                    "cim": {
                        "@version": "4.20.2",
                        "models": {},
                        "exceptions": {
                            "field": [
                                {
                                    "@name": "mane_1",
                                    "@value": "value_1",
                                    "@reason": "reason_1",
                                },
                                {
                                    "@name": "dest",
                                    "@value": "192.168.0.1",
                                    "@reason": "reason",
                                },
                            ]
                        },
                    }
                },
                {
                    "cim_version": "4.20.2",
                    "cim_fields": {},
                    "datamodels": {},
                    "exceptions": {"mane_1": "value_1", "dest": "192.168.0.1"},
                    "missing_recommended_fields": [],
                },
            ),
        ],
        ids=[
            "event-empty-directory",
            "event-no-cim",
            "event-full-cim",
            "event-with-exceptions",
        ],
    )
    def test_populate_requirement_test_data(self, sample_stanza, event, expected):
        ss = sample_stanza()
        assert ss.populate_requirement_test_data(event) == expected
