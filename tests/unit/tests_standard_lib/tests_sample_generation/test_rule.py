from collections import namedtuple
from unittest.mock import MagicMock, ANY

import pytest

import pytest_splunk_addon.standard_lib.sample_generation.rule

TOKEN_DATA = "token_data"
FIELD = "Field"
EVENTGEN_PARAMS = {"eventgen_params": "eventgen_params_value"}
SAMPLE_PATH = "sample_path"
SAMPLE_NAME = "Sample_name"
RETURN_VALUE = "Return_value"
IPV4 = "IPv4"
IPV6 = "IPv4"
FQDN = "fqdn"
REPL = "repl"

TokenValue = namedtuple("TokenValue", ["value"])


def token(replacement=REPL, replacement_type="static"):
    return {
        "token": TOKEN_DATA,
        "replacement": replacement,
        "replacementType": replacement_type,
        "field": FIELD,
    }


def test_raise_warning(caplog):
    warning_message = "Warning_message"
    pytest_splunk_addon.standard_lib.sample_generation.rule.raise_warning(
        warning_message
    )
    assert caplog.messages == [warning_message]


@pytest.fixture
def event():
    def func(token_count=1):
        eve = MagicMock()
        eve.sample_name = SAMPLE_NAME
        eve.get_token_count.return_value = token_count
        eve.replacement_map = {}
        return eve

    return func


class TestRule:
    @pytest.fixture
    def rule(self):
        return pytest_splunk_addon.standard_lib.sample_generation.rule.Rule(token())

    @pytest.fixture
    def mock_class(self, monkeypatch):
        def func(class_to_mock):
            class_mock = MagicMock()
            class_mock.return_value = RETURN_VALUE
            monkeypatch.setattr(
                f"pytest_splunk_addon.standard_lib.sample_generation.rule.{class_to_mock}",
                class_mock,
            )
            return class_mock

        return func

    @pytest.mark.parametrize(
        "rule_name, _token, params, params_dict",
        [
            ("StaticRule", token(), [token()], {}),
            (
                "TimeRule",
                token(replacement_type="timestamp"),
                [token(replacement_type="timestamp"), EVENTGEN_PARAMS],
                {},
            ),
            (
                "FileRule",
                token(replacement_type="file"),
                [token(replacement_type="file")],
                {"sample_path": SAMPLE_PATH},
            ),
            (
                "FileRule",
                token(replacement_type="mvfile"),
                [token(replacement_type="mvfile")],
                {"sample_path": SAMPLE_PATH},
            ),
            (
                "HexRule",
                token(replacement_type="random", replacement="hex"),
                [token(replacement_type="random", replacement="hex")],
                {"sample_path": SAMPLE_PATH},
            ),
            (
                "ListRule",
                token(replacement_type="all", replacement="list_repl"),
                [token(replacement_type="all", replacement="list_repl")],
                {"sample_path": SAMPLE_PATH},
            ),
            (
                "Ipv4Rule",
                token(replacement_type="all", replacement="ipv4"),
                [token(replacement_type="random", replacement="ipv4")],
                {"sample_path": SAMPLE_PATH},
            ),
        ],
    )
    def test_parse_rule(self, rule, mock_class, rule_name, _token, params, params_dict):
        static_mock = mock_class(rule_name)
        assert rule.parse_rule(_token, EVENTGEN_PARAMS, SAMPLE_PATH) == RETURN_VALUE
        static_mock.assert_called_once_with(*params, **params_dict)

    def test_parse_rule_other_repl_type(self, rule):
        assert (
            rule.parse_rule(
                token(replacement_type="other", replacement="dest"),
                EVENTGEN_PARAMS,
                SAMPLE_PATH,
            )
            is None
        )

    def test_apply_replacement_type_all(self, mock_class, event):
        sample_event_mock = mock_class("SampleEvent")
        return_event_1 = MagicMock()
        return_event_2 = MagicMock()
        sample_event_mock.copy.side_effect = [return_event_1, return_event_2]
        replace_mock = MagicMock()
        token_values = [[TokenValue(1)], [TokenValue(2)]]
        replace_mock.side_effect = token_values
        rule = pytest_splunk_addon.standard_lib.sample_generation.rule.Rule(
            token(replacement_type="all")
        )
        rule.replace = replace_mock
        event1 = event()
        event2 = event()
        events = [event1, event2]
        assert rule.apply(events) == [return_event_1, return_event_2]
        assert (
            pytest_splunk_addon.standard_lib.sample_generation.rule.event_host_count
            == 2
        )
        for e, tv in zip(
            [return_event_1, return_event_2], [TokenValue(1), TokenValue(2)]
        ):
            e.replace_token.assert_called_once_with(TOKEN_DATA, tv.value)
            e.register_field_value.assert_called_once_with(FIELD, tv)

    def test_apply_replacement_type_not_all(self, event):
        replace_mock = MagicMock()
        token_values = [[TokenValue(1)], [TokenValue(2)], [TokenValue(3)]]
        replace_mock.side_effect = token_values
        rule = pytest_splunk_addon.standard_lib.sample_generation.rule.Rule(
            token(replacement_type="random")
        )
        rule.replace = replace_mock
        event1 = event()
        event2 = event()
        event3 = event(token_count=0)
        events = [event1, event2, event3]
        assert rule.apply(events) == events
        for e, tv in zip(events[:2], token_values[:2]):
            e.replace_token.assert_called_once_with(TOKEN_DATA, tv)
            e.register_field_value.assert_called_once_with(FIELD, tv)
        assert not event3.replace_token.called
        assert not event3.register_field_value.called

    def test_get_lookup_value(self, rule, event):
        eve = event()
        test_key = "test_key"
        header_2 = "header2"
        headers = ["header1", header_2]
        one = "one"
        csv_template = [
            "user{}",
            "user{}@email.com",
            r"sample_domain.com\user{}",
            "CN=user{}",
        ]

        def create_csv(value):
            return [e.format(value) for e in csv_template]

        def validate(value_list, index_list, csv, email_count, result_csv):
            assert rule.get_lookup_value(eve, test_key, headers, value_list) == (
                index_list,
                csv,
            )
            pytest_splunk_addon.standard_lib.sample_generation.rule.user_email_count = (
                email_count
            )
            assert eve.replacement_map == {test_key: result_csv}

        csv_row_1 = create_csv("1")
        validate([one, header_2], [1], csv_row_1, 1, [csv_row_1])
        csv_row_2 = create_csv("2")
        validate([one] + headers, [0, 1], csv_row_2, 2, [csv_row_1, csv_row_2])

    @pytest.mark.parametrize(
        "value_list, expected",
        [
            (["host", "more"], [FIELD]),
            (["host1", "ipv4", "ipv6"], [IPV4, IPV6]),
            ([FQDN], [FQDN]),
            (["one", "two", "three"], []),
        ],
    )
    def test_get_rule_replacement_values(self, rule, value_list, expected):
        sample = MagicMock()
        sample.get_field_host.side_effect = [FIELD]
        sample.get_ipv4.side_effect = [IPV4]
        sample.get_ipv6.side_effect = [IPV6]
        sample.get_field_fqdn.side_effect = [FQDN]
        assert rule.get_rule_replacement_values(sample, value_list, ANY) == expected

    def test_clean_rules(self, rule):
        pytest_splunk_addon.standard_lib.sample_generation.rule.event_host_count = 25
        assert (
            pytest_splunk_addon.standard_lib.sample_generation.rule.event_host_count
            == 25
        )
        rule.clean_rules()
        assert (
            pytest_splunk_addon.standard_lib.sample_generation.rule.event_host_count
            == 0
        )


@pytest.mark.parametrize(
    "repl_type, repl, expected",
    [
        ("random", "integer[30:212]", ([44, 44], [44, 44])),
        ("all", "Integer[4:7]", (["4", "4"], ["5", "5"], ["6", "6"])),
    ],
)
def test_int_rule(event, monkeypatch, repl_type, repl, expected):
    rule = pytest_splunk_addon.standard_lib.sample_generation.rule.IntRule(
        token(replacement=repl, replacement_type=repl_type)
    )
    eve = event()
    monkeypatch.setattr(
        pytest_splunk_addon.standard_lib.sample_generation.rule,
        "randint",
        MagicMock(return_value=44),
    )
    assert list(rule.replace(eve, 2)) == [rule.token_value(i, j) for i, j in expected]


def test_int_rule_no_match(event, caplog):
    rule = pytest_splunk_addon.standard_lib.sample_generation.rule.IntRule(token())
    eve = event()
    assert list(rule.replace(eve, 40)) == []
    assert caplog.messages == [
        f"Non-supported format: '{REPL}' in stanza '{SAMPLE_NAME}'.\n Try integer[0:10]"
    ]
