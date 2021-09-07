import datetime
from collections import namedtuple
from unittest.mock import ANY, MagicMock, call, mock_open, patch

import pytest
import pytz
from freezegun import freeze_time

import pytest_splunk_addon.standard_lib.sample_generation.rule

TOKEN_DATA = "token_data"
FIELD = "Field"
EVENTGEN_PARAMS = {"eventgen_params": "eventgen_params_value"}
SAMPLE_PATH = "sample_path"
SAMPLE_NAME = "Sample_name"
RETURN_VALUE = "Return_value"
IPV4 = "IPv4"
IPV6 = "IPv4"
IPV4_LOWER = "ipv4"
IPV6_LOWER = "ipv6"
FQDN = "fqdn"
REPL = "repl"
INT = "int"
FLOAT = "float"
LIST = "list"
STATIC = "static"
FILE = "file"
TIME = "time"
MAC_ADDRESS = "mac_address"
GUID = "guid"
USER = "user"
EMAIL = "email"
URL = "url"
DEST = "dest"
SRCPORT = "srcport"
DVC = "dvc"
SRC = "src"
DESTPORT = "destport"
HOST = "host"
HEX = "hex"
ALL = "all"
RANDOM = "random"
CHOICE = "choice"
ELEM_1 = "elem_1"
ELEM_2 = "elem_2"
ELEM_3 = "elem_3"
DUMMY_FILE_PATH = "/dummy/path/to/file"

TokenValue = namedtuple("TokenValue", ["value"])
token_value = namedtuple("token_value", ["key", "value"])
mocked_datetime = datetime.datetime(2021, 3, 26, 18, 18, 46, 1, pytz.UTC)


def token(replacement=REPL, replacement_type=STATIC):
    return {
        "token": TOKEN_DATA,
        "replacement": replacement,
        "replacementType": replacement_type,
        "field": FIELD,
    }


def get_patch(func, return_value):
    return patch(
        f"pytest_splunk_addon.standard_lib.sample_generation.rule.{func}",
        MagicMock(return_value=return_value),
    )


def test_raise_warning(caplog):
    warning_message = "Warning_message"
    pytest_splunk_addon.standard_lib.sample_generation.rule.raise_warning(
        warning_message
    )
    assert caplog.messages == [warning_message]


def get_rule_class(name):
    rule_module = pytest_splunk_addon.standard_lib.sample_generation.rule
    rule_classes = {
        INT: rule_module.IntRule,
        FLOAT: rule_module.FloatRule,
        LIST: rule_module.ListRule,
        STATIC: rule_module.StaticRule,
        FILE: rule_module.FileRule,
        TIME: rule_module.TimeRule,
        IPV4_LOWER: rule_module.Ipv4Rule,
        IPV6_LOWER: rule_module.Ipv6Rule,
        MAC_ADDRESS: rule_module.MacRule,
        GUID: rule_module.GuidRule,
        USER: rule_module.UserRule,
        EMAIL: rule_module.EmailRule,
        URL: rule_module.UrlRule,
        DEST: rule_module.DestRule,
        SRCPORT: rule_module.SrcPortRule,
        DVC: rule_module.DvcRule,
        SRC: rule_module.SrcRule,
        DESTPORT: rule_module.DestPortRule,
        HOST: rule_module.HostRule,
        HEX: rule_module.HexRule,
    }
    return rule_classes[name]


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
                token(replacement_type=FILE),
                [token(replacement_type=FILE)],
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
                token(replacement_type=RANDOM, replacement=HEX),
                [token(replacement_type=RANDOM, replacement=HEX)],
                {"sample_path": SAMPLE_PATH},
            ),
            (
                "ListRule",
                token(replacement_type=ALL, replacement="list_repl"),
                [token(replacement_type=ALL, replacement="list_repl")],
                {"sample_path": SAMPLE_PATH},
            ),
            (
                "Ipv4Rule",
                token(replacement_type=ALL, replacement=IPV4_LOWER),
                [token(replacement_type=RANDOM, replacement=IPV4_LOWER)],
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
                token(replacement_type="other", replacement=DEST),
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
            token(replacement_type=ALL)
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
            token(replacement_type=RANDOM)
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
            ([HOST, "more"], [FIELD]),
            (["host1", IPV4_LOWER, IPV6_LOWER], [IPV4, IPV6]),
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
    "repl_type, repl, expected, class_name, to_mock, ret_value",
    [
        (RANDOM, "integer[30:212]", ([44, 44], [44, 44]), INT, "randint", 44),
        (
            ALL,
            "Integer[4:7]",
            (["4", "4"], ["5", "5"], ["6", "6"]),
            INT,
            "randint",
            44,
        ),
        (
            RANDOM,
            "float[13.55:664.545]",
            ([22.33, 22.33], [22.33, 22.33]),
            FLOAT,
            "uniform",
            22.331,
        ),
        (
            RANDOM,
            "Float[13:664.545]",
            ([22.3, 22.3], [22.3, 22.3]),
            FLOAT,
            "uniform",
            22.331,
        ),
        (
            RANDOM,
            "List['elem_1', 'elem_2']",
            ([ELEM_1, ELEM_1], [ELEM_1, ELEM_1]),
            LIST,
            CHOICE,
            ELEM_1,
        ),
        (
            ALL,
            "list['elem_1', 'elem_2']",
            ([ELEM_1, ELEM_1], [ELEM_2, ELEM_2]),
            LIST,
            CHOICE,
            ELEM_1,
        ),
        (
            ALL,
            ELEM_3,
            ([ELEM_3, ELEM_3], [ELEM_3, ELEM_3]),
            STATIC,
            CHOICE,
            ELEM_1,
        ),
    ],
)
def test_rule(
    event, monkeypatch, repl_type, repl, expected, class_name, to_mock, ret_value
):
    rule = get_rule_class(class_name)(
        token(replacement=repl, replacement_type=repl_type)
    )
    eve = event()
    monkeypatch.setattr(
        pytest_splunk_addon.standard_lib.sample_generation.rule,
        to_mock,
        MagicMock(return_value=ret_value),
    )
    assert list(rule.replace(eve, 2)) == [rule.token_value(i, j) for i, j in expected]


@pytest.mark.parametrize(
    "class_name, return_value",
    [
        (IPV4_LOWER, "192.168.1.1"),
        (IPV6_LOWER, "2001:0db8:0000:0000:0000:ff00:0042:8329"),
        (MAC_ADDRESS, "AA-00-04-00-XX-YY"),
    ],
)
def test_ip_rule(event, class_name, return_value):
    eve = event()
    rule = get_rule_class(class_name)(token())
    with patch.object(rule.fake, class_name, MagicMock(return_value=return_value)):
        assert list(rule.replace(eve, 2)) == [
            token_value(key=return_value, value=return_value),
            token_value(key=return_value, value=return_value),
        ]


def test_guid_rule(event):
    eve = event()
    rule = get_rule_class(GUID)(token())
    _uuid = "123e4567-e89b-12d3-a456-426614174000"
    with get_patch("uuid.uuid4", _uuid):
        assert list(rule.replace(eve, 2)) == [
            token_value(key=_uuid, value=_uuid),
            token_value(key=_uuid, value=_uuid),
        ]


@pytest.mark.parametrize(
    "class_name, warning_message",
    [
        (
            INT,
            f"Non-supported format: '{REPL}' in stanza '{SAMPLE_NAME}'.\n Try integer[0:10]",
        ),
        (
            FLOAT,
            f"Non-supported format: '{REPL}' in stanza '{SAMPLE_NAME}'.\n i.e float[0.00:70.00]",
        ),
        (
            LIST,
            f"Non-supported format: '{REPL}' in stanza '{SAMPLE_NAME}'.\n Try  list['value1','value2']",
        ),
    ],
)
def test_int_rule_no_match(event, caplog, class_name, warning_message):
    rule = get_rule_class(class_name)(token())
    eve = event()
    assert list(rule.replace(eve, 40)) == []
    assert caplog.messages == [warning_message]


class TestFileRule:
    @pytest.mark.parametrize("index_sample_se", [(ELEM_1, ELEM_2), ValueError])
    def test_replace(self, event, index_sample_se):
        eve = event()
        rule = get_rule_class(FILE)(token())
        rule.get_file_path = MagicMock(return_value=(DUMMY_FILE_PATH, "2"))
        rule.indexed_sample_file = MagicMock(side_effect=[index_sample_se])
        token_value_mock = MagicMock(return_value=TOKEN_DATA)
        rule.token_value = token_value_mock
        rule.lookupfile = MagicMock(return_value=(ELEM_1, ELEM_2))
        assert list(rule.replace(eve, 4)) == [TOKEN_DATA] * 2
        token_value_mock.assert_has_calls([call(ELEM_1, ELEM_1), call(ELEM_2, ELEM_2)])

    @pytest.mark.parametrize(
        "replacement_type, token_cnt, expected",
        [
            (RANDOM, 2, [call(ELEM_1, ELEM_1), call(ELEM_1, ELEM_1)]),
            (
                ALL,
                3,
                [
                    call(ELEM_1, ELEM_1),
                    call(ELEM_2, ELEM_2),
                    call(ELEM_3, ELEM_3),
                ],
            ),
        ],
    )
    def test_replace_index_not_set(self, event, replacement_type, token_cnt, expected):
        eve = event()
        rule = get_rule_class(FILE)(token(replacement_type=replacement_type))
        rule.get_file_path = MagicMock(return_value=(DUMMY_FILE_PATH, 0))
        token_value_mock = MagicMock(return_value=TOKEN_DATA)
        rule.token_value = token_value_mock
        data = f"{ELEM_1}\n{ELEM_2}\n{ELEM_3}"
        with patch("builtins.open", mock_open(read_data=data)), get_patch(
            CHOICE, ELEM_1
        ):
            assert list(rule.replace(eve, 2)) == [TOKEN_DATA] * token_cnt
            token_value_mock.assert_has_calls(expected)

    def test_replace_error(self, event, caplog):
        eve = event()
        rule = get_rule_class(FILE)(token())
        rule.get_file_path = MagicMock(return_value=(DUMMY_FILE_PATH, 0))
        with patch("builtins.open", MagicMock(side_effect=IOError)):
            assert list(rule.replace(eve, 2)) == []
            assert caplog.messages == ["File not found : /dummy/path/to/file"]

    @pytest.mark.parametrize(
        "repl, sample_path, isfile_mock_value, expected",
        [
            (
                "file[/dir/apps/middle/dir:fls]",
                "/files/apps/samples/rest",
                True,
                ("/files/apps/dir", "fls"),
            ),
            (
                "file[/dir/apps/middle/dir]",
                "/Files/apps/samples/rest",
                True,
                ("/Files/apps/dir", None),
            ),
            (
                "/dir/apps/middle/dir:fls",
                "/Files/apps/samples/rest",
                True,
                ("/Files/apps/dir", "fls"),
            ),
            (
                "file[/dir/apps/middle/dir]",
                "/Files/apps/samples/rest",
                False,
                ("/dir/apps/middle/dir", None),
            ),
            (
                "File[/dir/apps/middle/dir:fls1:fls2]",
                "/Files/apps/samples/rest",
                False,
                ("/dir/apps/middle/dir:fls1", "fls2"),
            ),
        ],
    )
    def test_get_file_path(
        self, event, monkeypatch, repl, sample_path, isfile_mock_value, expected
    ):
        monkeypatch.setattr("os.sep", "/")
        rule = get_rule_class(FILE)(
            token(replacement_type="_", replacement=repl), sample_path=sample_path
        )
        with patch("os.path.join") as join_mock, patch("os.path.isfile") as isfile_mock:
            join_mock.side_effect = lambda *x: "/".join(x)
            isfile_mock.return_value = isfile_mock_value
            assert rule.get_file_path() == expected

    @pytest.mark.parametrize(
        "replacement_map, data, expected, file_count",
        [
            (
                {"path": {"data": ["one, two, three", "_"]}},
                "data1\ndata2\n\ndata3",
                "one",
                0,
            ),
            (
                {"path": {"data": ["one, two, three", "_"], "find_all": True}},
                "data1\ndata2\n\ndata3",
                "one",
                1,
            ),
            (
                {"path": {"data": ["one, two, three", "_"], "find_all": True}},
                "data1",
                "one",
                0,
            ),
            (
                {"path1": {"data": [",data1", ",data2", ",data3"], "find_all": True}},
                ",data1\nfirst,data2\n\n,data3",
                "first",
                0,
            ),
        ],
    )
    def test_indexed_sample_file(
        self, event, replacement_map, data, expected, file_count
    ):
        rule = get_rule_class(FILE)(token())
        eve = event()
        eve.replacement_map = replacement_map
        with patch("builtins.open", mock_open(read_data=data)), patch(
            "random.randint"
        ) as random_mock:
            random_mock.return_value = 1
            assert list(rule.indexed_sample_file(eve, "path", 1, 2)) == [expected] * 2
            assert rule.file_count == file_count

    @pytest.mark.parametrize(
        "replacement_type, replacement_map, data, expected, file_count",
        [
            (
                ALL,
                {"path": {"data": [",data1", ",data2", ",data3"], "find_all": True}},
                ",data1\n,data2\n\n,data3",
                ["data1", "data2", "data3"],
                0,
            ),
            (
                RANDOM,
                {"path": {"data": [",data2"]}},
                ",data1\n,data2\n\n,data3",
                ["data2"] * 3,
                0,
            ),
        ],
    )
    def test_indexed_sample_file_no_replacement_map(
        self, event, replacement_type, replacement_map, data, expected, file_count
    ):
        rule = get_rule_class(FILE)(token(replacement_type=replacement_type))
        eve = event()
        del eve.replacement_map
        with patch("builtins.open", mock_open(read_data=data)), patch(
            "random.randint"
        ) as random_mock:
            random_mock.return_value = 1
            assert list(rule.indexed_sample_file(eve, "path", 2, 3)) == expected
            assert rule.file_count == file_count
            assert eve.replacement_map == replacement_map

    @pytest.mark.parametrize(
        "err, err_msg",
        [
            (IndexError, "Index for column 4 in replacementfile path is out of bounds"),
            (IOError, "File not found : path"),
        ],
    )
    def test_indexed_sample_errors(self, caplog, event, err, err_msg):
        rule = get_rule_class(FILE)(token())
        eve = event()
        with patch("builtins.open", mock_open()) as mo:
            mo.side_effect = err
            assert list(rule.indexed_sample_file(eve, "path", 4, 5)) == []
            assert caplog.messages == [err_msg]

    @pytest.mark.parametrize(
        "replacement_type, replacement_map, data, del_repl_map, expected, file_count",
        [
            (
                RANDOM,
                {"path": ["header_1,header_2,header_3\n", "field3,data3"]},
                "header_1,header_2,header_3\n,data2\n\nfield3,data3",
                True,
                ["data3"],
                1,
            ),
            (
                ALL,
                None,
                "header_1,header_2,header_3\n,data2\n\nfield3,data3",
                True,
                [TOKEN_DATA],
                0,
            ),
            (
                ALL,
                {"path": ["header_1,header_2,header_3\n", "field3,data3"]},
                "header_1,header_2,header_3\n,data2\n\nfield3,data3",
                False,
                ["data3"],
                0,
            ),
        ],
    )
    def test_lookupfile(
        self,
        event,
        replacement_type,
        replacement_map,
        data,
        del_repl_map,
        expected,
        file_count,
    ):
        rule = get_rule_class(FILE)(token(replacement_type=replacement_type))
        eve = event()
        eve.replacement_map = replacement_map
        if del_repl_map:
            del eve.replacement_map
        with patch("builtins.open", mock_open(read_data=data)), patch(
            "random.randint"
        ) as random_mock:
            random_mock.return_value = 1
            assert list(rule.lookupfile(eve, "path", "header_2", 1)) == expected
            assert rule.file_count == file_count
            assert getattr(eve, "replacement_map", None) == replacement_map

    @pytest.mark.parametrize(
        "err, err_msg",
        [
            (ValueError, "Column '4' is not present replacement file 'path'"),
            (IOError, "File not found : path"),
        ],
    )
    def test_lookup_file_errors(self, caplog, event, err, err_msg):
        rule = get_rule_class(FILE)(token())
        eve = event()
        with patch("builtins.open", mock_open()) as mo:
            mo.side_effect = err
            assert list(rule.lookupfile(eve, "path", 4, 5)) == []
            assert caplog.messages == [err_msg]


class TestTimeRule:
    @freeze_time("2020-11-01T04:16:13-04:00")
    @pytest.mark.parametrize(
        "earliest, latest, expected",
        [
            (
                "24h",
                "6h",
                [
                    token_value(key=1616779126, value=REPL),
                    token_value(key=1616779126, value=REPL),
                    token_value(key=1616779126, value=REPL),
                ],
            ),
            (
                "now",
                None,
                [
                    token_value(key=1616779126, value=REPL),
                    token_value(key=1616779126, value=REPL),
                    token_value(key=1616779126, value=REPL),
                ],
            ),
            (
                "+10000",
                "+10000",
                [
                    token_value(key=1616779126.0, value=REPL),
                    token_value(key=1616779126.0, value=REPL),
                    token_value(key=1616779126.0, value=REPL),
                ],
            ),
        ],
    )
    def test_replace(self, event, earliest, latest, expected):
        eve = event()
        rule = get_rule_class(TIME)(
            token(), eventgen_params={"earliest": earliest, "latest": latest}
        )
        with get_patch("time_parse.convert_to_time", mocked_datetime), get_patch(
            "randint", 1439905910
        ), get_patch("datetime.fromtimestamp", mocked_datetime), get_patch(
            "mktime", 1616779126
        ) as mktime_mock:
            assert list(rule.replace(eve, 3)) == expected
            mktime_mock.assert_has_calls([call(mocked_datetime.timetuple())] * 3)

    @freeze_time("2020-11-01T04:16:13-04:00")
    @pytest.mark.parametrize(
        "timezone, replacement, expected",
        [
            (
                "local",
                REPL,
                [
                    token_value(key=1616779126.0, value=REPL),
                    token_value(key=1616779126.0, value=REPL),
                ],
            ),
            (
                "0001",
                "%s",
                [
                    token_value(key=1616779126.0, value="1616779126"),
                    token_value(key=1616779126.0, value="1616779126"),
                ],
            ),
        ],
    )
    def test_replace_local_timezone(self, event, timezone, replacement, expected):
        eve = event()
        rule = get_rule_class(TIME)(
            token(replacement=replacement),
            eventgen_params={"earliest": "24h", "latest": "6h", "timezone": timezone},
        )
        with get_patch("time_parse.convert_to_time", mocked_datetime), get_patch(
            "randint", 1616801099
        ), get_patch("time_parse.get_timezone_time", mocked_datetime), patch.object(
            rule, "invert_timezone", MagicMock(return_value="0000")
        ), get_patch(
            "mktime", 1616779126
        ) as mktime_mock:
            assert list(rule.replace(eve, 2)) == expected
            mktime_mock.assert_has_calls([call(mocked_datetime.timetuple())] * 2)

    @pytest.mark.parametrize(
        "timezone_time, expected",
        [("0000", "0000"), ("-12345", "+2345"), ("+12345", "-2345")],
    )
    def test_invert_timezone(self, timezone_time, expected):
        rule = get_rule_class(TIME)(token())
        assert rule.invert_timezone(timezone_time) == expected

    def test_invert_timezone_error(self):
        rule = get_rule_class(TIME)(token())
        with pytest.raises(Exception, match="Invalid timezone value found."):
            rule.invert_timezone("1234")


@pytest.mark.parametrize(
    "class_name, replacement, replacement_map, index_list, expected",
    [
        (
            USER,
            "User[22]",
            {},
            [1, 2],
            [
                token_value(key="two", value="two"),
                token_value(key="two", value="two"),
            ],
        ),
        (
            USER,
            "user['name']",
            {EMAIL: [[1, 2, 3], [1, 2, 3], [1, 2, 3]]},
            [1, 2],
            [token_value(key=2, value=2), token_value(key=2, value=2)],
        ),
        (
            USER,
            "User[22]",
            {},
            [],
            [],
        ),
        (
            USER,
            "Wrong[22]",
            {},
            [],
            [],
        ),
        (
            EMAIL,
            "",
            {},
            [],
            [
                token_value(key="two", value="two"),
                token_value(key="two", value="two"),
            ],
        ),
        (
            EMAIL,
            "",
            {USER: [[1, 2, 3], [1, 2, 3], [1, 2, 3]]},
            [],
            [token_value(key=2, value=2), token_value(key=2, value=2)],
        ),
    ],
)
def test_user_and_email_rule(
    event, class_name, replacement, replacement_map, index_list, expected
):
    rule = get_rule_class(class_name)(token(replacement=replacement))
    eve = event()
    eve.replacement_map = replacement_map
    with patch.object(
        rule,
        "get_lookup_value",
        MagicMock(return_value=(index_list, ["one", "two", "three"])),
    ), get_patch(CHOICE, 1):
        assert list(rule.replace(eve, 2)) == expected


class TestUrlRule:
    @pytest.mark.parametrize(
        "replacement, expected",
        [
            ("Url['name']", []),
            (
                "Url['ip_host', 'fqdn_host', 'path', 'query', 'protocol', 'full']",
                [
                    token_value(
                        key="aa/a?aaa=aaa&aaa=aaa&aaa=aaa",
                        value="aa/a?aaa=aaa&aaa=aaa&aaa=aaa",
                    ),
                    token_value(
                        key="aa/a?aaa=aaa&aaa=aaa&aaa=aaa",
                        value="aa/a?aaa=aaa&aaa=aaa&aaa=aaa",
                    ),
                ],
            ),
            ("Wrong['name']", []),
            (
                "Url[]",
                [
                    token_value(key="http://example.com", value="http://example.com"),
                    token_value(key="http://example.com", value="http://example.com"),
                ],
            ),
        ],
    )
    def test_replace(self, event, replacement, expected):
        eve = event()
        rule = get_rule_class(URL)(token(replacement=replacement))
        with get_patch(CHOICE, "a"), get_patch("randint", 3), patch.object(
            rule.fake,
            URL,
            MagicMock(return_value="http://example.com"),
        ):
            assert list(rule.replace(eve, 2)) == expected

    def test_generate_url_query_params(self):
        rule = get_rule_class(URL)(token())
        with get_patch(CHOICE, "a"), get_patch("randint", 3):
            assert rule.generate_url_query_params() == "?aaa=aaa&aaa=aaa&aaa=aaa"


class TestDestDvcSrcRules:
    @pytest.mark.parametrize(
        "class_name, replacement, replacement_values, expected",
        [
            (
                DEST,
                "Dest['value1']",
                [ELEM_1, ELEM_2],
                [
                    token_value(key=ELEM_2, value=ELEM_2),
                    token_value(key=ELEM_2, value=ELEM_2),
                ],
            ),
            (
                DEST,
                "No['value1']",
                [ELEM_1, ELEM_2],
                [],
            ),
            (
                DEST,
                "dest['value1']",
                [],
                [],
            ),
            (
                DVC,
                "dvc['value1']",
                [ELEM_1, ELEM_2],
                [
                    token_value(key=ELEM_2, value=ELEM_2),
                    token_value(key=ELEM_2, value=ELEM_2),
                ],
            ),
            (
                DVC,
                "No['value1']",
                [ELEM_1, ELEM_2],
                [],
            ),
            (
                DVC,
                "Dvc['value1']",
                [],
                [],
            ),
            (
                SRC,
                "Src['value1']",
                [ELEM_1, ELEM_2],
                [
                    token_value(key=ELEM_2, value=ELEM_2),
                    token_value(key=ELEM_2, value=ELEM_2),
                ],
            ),
            (
                SRC,
                "No['value1']",
                [ELEM_1, ELEM_2],
                [],
            ),
            (
                SRC,
                "src['value1']",
                [],
                [],
            ),
        ],
    )
    def test_replace(
        self, event, class_name, replacement, replacement_values, expected
    ):
        eve = event()
        rule = get_rule_class(class_name)(token(replacement=replacement))
        with patch.object(
            rule,
            "get_rule_replacement_values",
            MagicMock(return_value=replacement_values),
        ), get_patch(CHOICE, ELEM_2):
            assert list(rule.replace(eve, 2)) == expected


class TestSrcPortRule:
    def test_replace(self, event):
        eve = event()
        rule = get_rule_class(SRCPORT)(token())
        with get_patch("randint", 4211):
            assert list(rule.replace(eve, 2)) == [
                token_value(key=4211, value=4211),
                token_value(key=4211, value=4211),
            ]


class TestDestPortRule:
    def test_replace(self, event):
        eve = event()
        rule = get_rule_class(DESTPORT)(token())
        with get_patch(CHOICE, 22):
            assert list(rule.replace(eve, 2)) == [
                token_value(key=22, value=22),
                token_value(key=22, value=22),
            ]


class TestHostRule:
    @pytest.mark.parametrize(
        "replacement, replacement_values, metadata, expected",
        [
            (
                "Host['host']",
                [HOST, ELEM_2],
                {"input_type": "syslog_tcp", HOST: "metadata_host"},
                [
                    token_value(key=ELEM_2, value=ELEM_2),
                    token_value(key=ELEM_2, value=ELEM_2),
                ],
            ),
            (
                "Host['host']",
                [HOST, ELEM_2],
                {"input_type": "file_monitor", HOST: "metadata_host"},
                [
                    token_value(key=ELEM_2, value=ELEM_2),
                    token_value(key=ELEM_2, value=ELEM_2),
                ],
            ),
            (
                "No['host']",
                [HOST, ELEM_2],
                {"input_type": "syslog_tcp", HOST: "metadata_host"},
                [],
            ),
            (
                "host['host']",
                [],
                {"input_type": "syslog_tcp", HOST: "metadata_host"},
                [],
            ),
        ],
    )
    def test_replace(self, event, replacement, replacement_values, metadata, expected):
        eve = event()
        eve.metadata = metadata
        eve.get_host = lambda: "host_1"
        rule = get_rule_class(HOST)(token(replacement=replacement))
        with patch.object(
            rule,
            "get_rule_replacement_values",
            MagicMock(return_value=replacement_values),
        ), get_patch(CHOICE, ELEM_2):
            assert list(rule.replace(eve, 2)) == expected


class TestHexRule:
    @pytest.mark.parametrize(
        "replacement, expected",
        [
            (
                "hex(3)",
                [
                    token_value(key="888", value="888"),
                    token_value(key="888888", value="888888"),
                ],
            ),
            ("not_correct(3)", []),
            ("Hex(3m)", []),
        ],
    )
    def test_replace(self, event, replacement, expected):
        eve = event()
        rule = get_rule_class(HEX)(token(replacement=replacement))
        with get_patch("randint", 8):
            assert list(rule.replace(eve, 2)) == expected
