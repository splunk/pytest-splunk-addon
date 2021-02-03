import sys
from collections import namedtuple
import pytest
from unittest.mock import MagicMock, call, patch

PropsProperty = namedtuple("PropsProperty", ["name", "value"])


@pytest.fixture
def field_mock(monkeypatch):
    field = MagicMock()
    monkeypatch.setattr(
        "pytest_splunk_addon.standard_lib.addon_parser.props_parser.Field", field
    )
    return field


@pytest.fixture
def transforms_parser(monkeypatch):
    tp = MagicMock
    monkeypatch.setattr(
        "pytest_splunk_addon.standard_lib.addon_parser.props_parser.TransformsParser",
        tp,
    )
    return tp


@pytest.fixture
def pp(field_mock, transforms_parser):
    import pytest_splunk_addon.standard_lib.addon_parser.props_parser as pp

    return pp.PropsParser


@pytest.fixture
def headers():
    return [
        "##",
        "## SPDX-FileCopyrightText: 2020 Splunk, Inc. <sales@splunk.com>",
        "## SPDX-License-Identifier: LicenseRef-Splunk-1-2020",
        "##",
        "##",
        "",
    ]


@pytest.fixture
def sect_value(mocker):
    return {
        "header": mocker.ANY,
        "lineno": mocker.ANY,
        "name": mocker.ANY,
        "options": mocker.ANY,
    }


@pytest.fixture
def sects(sect_value):
    return {
        "(?:::){0}snow:*": sect_value,
        "snow:incident": sect_value,
        "snow:change_request": sect_value,
        "snow:change_task": sect_value,
        "snow:problem": sect_value,
        "snow:em_event": sect_value,
        "snow:sys_user_group": sect_value,
        "snow:sys_user": sect_value,
        "snow:cmn_location": sect_value,
        "snow:cmdb_ci": sect_value,
        "snow:sys_choice": sect_value,
        "source::...ta_snow_setup.log*": sect_value,
        "source::...ta_snow_ticket.log*": sect_value,
        "source::...ta_snow_main.log*": sect_value,
        "source::...ta_snow_util.log*": sect_value,
    }


@pytest.fixture
def conf_file(configuration_file, headers, sects):
    def func(hs=None, ss=None, es=None):
        if hs is None:
            hs = headers
        if ss is None:
            ss = sects
        if es is None:
            es = []
        return configuration_file(headers=hs, sects=ss, errors=es)

    return func


def test_conf_file(conf_file):
    conf_file(hs=["11", "222"])


@pytest.fixture()
def props_parser(pp, fake_app, mocker):
    def func(cf):
        return pp(mocker.ANY, fake_app(cf))

    return func


@pytest.fixture
def default_props_parser(props_parser, conf_file):
    return props_parser(conf_file())


@pytest.fixture
def get_sects(sect_value):
    def func(sects_keys, sv=None):
        if sv is None:
            sv = sect_value
        return {k: sv for k in sects_keys}

    return func


@pytest.mark.parametrize(
    "src, expected",
    [
        ("source::...ta_snow_setup.log*", {"*ta_snow_setup.log*"}),
        ("source::...ta_snow_se...tup.log*", {"*ta_snow_se*tup.log*"}),
        ("source::...ta_(aa)_snow_(bb)setup.log*", {"*ta_aa_snow_bbsetup.log*"}),
        (
            "source::...ta_(aa|cc)_snow_(bb|mm)setup.log*",
            {
                "*ta_aa_snow_bbsetup.log*",
                "*ta_aa_snow_mmsetup.log*",
                "*ta_cc_snow_bbsetup.log*",
                "*ta_cc_snow_mmsetup.log*",
            },
        ),
    ],
)
def test_get_list_of_sources(default_props_parser, src, expected):
    assert set(list(default_props_parser.get_list_of_sources(src))) == expected


def test_get_sourcetype_assignments(default_props_parser, field_mock):
    pp = PropsProperty("Name", "Value")
    assert len(list(default_props_parser.get_sourcetype_assignments(pp))) == 1
    field_mock.assert_called_once()
    field_mock.assert_called_with({"name": "Name", "expected_values": ["Value"]})


@pytest.mark.parametrize(
    "lookup_str, expected",
    [
        (
            "field1 field2 OUTPUTNEW field3 field4 as field5",
            {
                "input_fields": ["field2"],
                "output_fields": ["field3", "field5"],
                "lookup_stanza": "field1",
            },
        ),
        (
            "field1 field2 field3 field4 as field5",
            {
                "input_fields": ["field2", "field3", "field5"],
                "output_fields": [],
                "lookup_stanza": "field1",
            },
        ),
        (
            "field1 field2 OUTPUT field3 field4 as field5",
            {
                "input_fields": ["field2"],
                "output_fields": ["field3", "field5"],
                "lookup_stanza": "field1",
            },
        ),
        (
            "field1 field2 OUTPUTNEW field3 field4 as field5 field6 as field7",
            {
                "input_fields": ["field2"],
                "output_fields": ["field3", "field5", "field7"],
                "lookup_stanza": "field1",
            },
        ),
        (
            "field1 field2 OUTPUTNEW field3 field4 as field5 OUTPUT field6 as field7",
            {
                "input_fields": ["field2"],
                "output_fields": ["field7"],
                "lookup_stanza": "field1",
            },
        ),
    ],
)
def test_parse_lookup_str(default_props_parser, lookup_str, expected):
    default_props_parser.parse_lookup_str(lookup_str)


def test_get_report_fields(default_props_parser, transforms_parser, mocker):
    pp = PropsProperty("Name", "Value, YYYYY,  AAAAAA GGGGG UUUUUUU , IIIIII")
    transforms_parser.get_transform_fields = MagicMock()
    assert list(default_props_parser.get_report_fields(pp)) == [
        ("Value", mocker.ANY),
        ("YYYYY", mocker.ANY),
        ("AAAAAA GGGGG UUUUUUU", mocker.ANY),
        ("IIIIII", mocker.ANY),
    ]
    transforms_parser.get_transform_fields.assert_has_calls(
        [call("Value"), call("YYYYY"), call("AAAAAA GGGGG UUUUUUU"), call("IIIIII")]
    )


def test_get_lookup_fields(default_props_parser):
    pp = PropsProperty(
        "Name",
        "field1 field2 OUTPUTNEW field3 field4 as field5 OUTPUT field6 as field7",
    )
    default_props_parser.parse_lookup_str = MagicMock(
        return_value={
            "input_fields": ["field2"],
            "output_fields": ["field7"],
            "lookup_stanza": "field1",
        }
    )
    fields_list = default_props_parser.get_lookup_fields.__wrapped__(
        default_props_parser, pp
    )
    assert len(fields_list) == 2
    assert "field2" in fields_list
    assert "field7" in fields_list


def test_get_lookup_fields_no_output_fields(default_props_parser):
    pp = PropsProperty("Name", "field1 field2 field3 field4 as field5")
    default_props_parser.parse_lookup_str = MagicMock(
        return_value={
            "input_fields": ["field2", "field3", "field5"],
            "output_fields": [],
            "lookup_stanza": "field1",
        }
    )
    default_props_parser.transforms_parser.get_lookup_csv_fields = MagicMock(
        return_value=("csv_field",)
    )
    fields_list = default_props_parser.get_lookup_fields.__wrapped__(
        default_props_parser, pp
    )
    assert len(fields_list) == 4
    assert "field2" in fields_list
    assert "field3" in fields_list
    assert "field5" in fields_list
    assert "csv_field" in fields_list


@pytest.mark.parametrize(
    "prop, expected",
    [
        (
            PropsProperty(
                "Name",
                "field1 as field2 field8",
            ),
            ("field1", "field2"),
        ),
        (
            PropsProperty(
                "Name",
                "field1 AS field2 field8",
            ),
            ("field1", "field2"),
        ),
        (
            PropsProperty(
                "Name",
                "field1 ASNEW field2 field8 field5 asnew field6",
            ),
            ("field1", "field2", "field5", "field6"),
        ),
        (
            PropsProperty(
                "Name",
                "field1 field2 ASNEW OUTPUTNEW field3 asnew fieldx field4 AS field5 field6 field7 as field8",
            ),
            (
                "field2",
                "OUTPUTNEW",
                "field3",
                "fieldx",
                "field4",
                "field5",
                "field7",
                "field8",
            ),
        ),
    ],
)
def test_get_fieldalias_fields(default_props_parser, prop, expected):
    fieldaliases = default_props_parser.get_fieldalias_fields.__wrapped__(
        default_props_parser, prop
    )
    assert len(fieldaliases) == len(expected)
    assert all(field in fieldaliases for field in expected)


@pytest.mark.parametrize(
    "prop, expected",
    [
        (PropsProperty("key EVAL-val", "EVAL-333 field1"), ["val"]),
        (PropsProperty("key EVAL-val", "null()"), []),
    ],
)
def test_get_eval_fields(default_props_parser, prop, expected):
    assert (
        list(
            default_props_parser.get_eval_fields.__wrapped__(default_props_parser, prop)
        )
        == expected
    )
