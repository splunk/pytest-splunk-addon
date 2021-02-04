from collections import namedtuple
import pytest
from unittest.mock import MagicMock, call

# helpers variables to make test input/outup easier to change
FIELD = "field"
FIELDS = f"{FIELD}s"
FIELD1 = f"{FIELD}1"
FIELD2 = f"{FIELD}2"
FIELD3 = f"{FIELD}3"
FIELD4 = f"{FIELD}4"
FIELD5 = f"{FIELD}5"
FIELD6 = f"{FIELD}6"
FIELD7 = f"{FIELD}7"
FIELD8 = f"{FIELD}8"
NAME = "Name"
OUTPUTNEW = "OUTPUTNEW"
OUTPUT = "OUTPUT"
INPUT_FIELDS = "input_fields"
OUTPUT_FIELDS = "output_fields"
STANZA = "stanza"
LOOKUP_STANZA = f"lookup_{STANZA}"
STANZA_TYPE = f"{STANZA}_type"
CLASSNAME = "classname"

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
        "## SPDX-FileCopyrightText: 2020 Splunk, Inc. <sales@splunk.com>",
        "## SPDX-License-Identifier: LicenseRef-Splunk-1-2020",
    ]


@pytest.fixture
def sect_value(mocker):
    SectValue = namedtuple("SectValue", ["header", "lineo", "name", "options"])
    options = {"REPORT": "report_value", "NON_report": "non_report_value"}

    def func(sect):
        return SectValue(mocker.ANY, mocker.ANY, sect, options)

    return func


@pytest.fixture
def sects(sect_value):
    scs = [
        "host::snow" "(?:::){0}snow:*",
        "snow:incident",
        "source::...ta_snow_setup.log*",
        "source::...ta_snow_ticket.log*",
    ]
    return {s: sect_value(s) for s in scs}


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


@pytest.fixture()
def props_parser(pp, fake_app, mocker):
    def func(cf):
        return pp(mocker.ANY, fake_app(cf))

    return func


@pytest.fixture
def default_props_parser(props_parser, conf_file):
    return props_parser(conf_file())


@pytest.fixture
def props_parser_empty_conf(pp, fake_app, conf_file, mocker):
    fa = fake_app(conf_file([], [], []))
    fa.props_conf.return_value = []
    return pp(mocker.ANY, fa)


@pytest.fixture
def get_sects(sect_value):
    def func(sects_keys, sv=None):
        if sv is None:
            sv = sect_value
        return {k: sv for k in sects_keys}

    return func


@pytest.fixture
def get_props_stanza_results(sect_value):
    return [
        ("sourcetype", "snow:incident", sect_value("snow:incident")),
        ("source", "*ta_snow_setup.log*1", sect_value("source::...ta_snow_setup.log*")),
        ("source", "*ta_snow_setup.log*2", sect_value("source::...ta_snow_setup.log*")),
        (
            "source",
            "*ta_snow_ticket.log*",
            sect_value("source::...ta_snow_ticket.log*"),
        ),
    ]


def test_get_props_fields(default_props_parser, get_props_stanza_results):
    gps = MagicMock()
    gps.return_value = get_props_stanza_results
    default_props_parser.get_props_stanzas = gps
    gpm = MagicMock()
    gpm.return_value = lambda x: (FIELD1, FIELD2)
    default_props_parser.get_props_method = gpm
    grf = MagicMock()
    grf.return_value = [("transform_string", (FIELD3, FIELD4))]
    default_props_parser.get_report_fields = grf
    assert list(default_props_parser.get_props_fields()) == [
        {
            STANZA: "snow:incident",
            STANZA_TYPE: "sourcetype",
            CLASSNAME: "REPORT::transform_string",
            FIELDS: [FIELD3, FIELD4],
        },
        {
            STANZA: "snow:incident",
            STANZA_TYPE: "sourcetype",
            CLASSNAME: "NON_report",
            FIELDS: [FIELD1, FIELD2],
        },
        {
            STANZA: "*ta_snow_setup.log*1",
            STANZA_TYPE: "source",
            CLASSNAME: "REPORT::transform_string",
            FIELDS: [FIELD3, FIELD4],
        },
        {
            STANZA: "*ta_snow_setup.log*1",
            STANZA_TYPE: "source",
            CLASSNAME: "NON_report",
            FIELDS: [FIELD1, FIELD2],
        },
        {
            STANZA: "*ta_snow_setup.log*2",
            STANZA_TYPE: "source",
            CLASSNAME: "REPORT::transform_string",
            FIELDS: [FIELD3, FIELD4],
        },
        {
            STANZA: "*ta_snow_setup.log*2",
            STANZA_TYPE: "source",
            CLASSNAME: "NON_report",
            FIELDS: [FIELD1, FIELD2],
        },
        {
            STANZA: "*ta_snow_ticket.log*",
            STANZA_TYPE: "source",
            CLASSNAME: "REPORT::transform_string",
            FIELDS: [FIELD3, FIELD4],
        },
        {
            STANZA: "*ta_snow_ticket.log*",
            STANZA_TYPE: "source",
            CLASSNAME: "NON_report",
            FIELDS: [FIELD1, FIELD2],
        },
    ]


@pytest.mark.parametrize(
    "class_name, expected",
    [
        ("extract", "extract_fields"),
        ("EVAL", "eval_fields"),
        ("FIELDalias", "fieldalias_fields"),
        ("lookup", "lookup_fields"),
        ("something", None),
    ],
)
def test_get_props_method(default_props_parser, class_name, expected, caplog):
    default_props_parser.get_extract_fields = "extract_fields"
    default_props_parser.get_eval_fields = "eval_fields"
    default_props_parser.get_fieldalias_fields = "fieldalias_fields"
    default_props_parser.get_lookup_fields = "lookup_fields"
    if expected is None:
        assert default_props_parser.get_props_method(class_name) is expected
        assert caplog.messages == ["No parser available for something. Skipping..."]
    else:
        assert default_props_parser.get_props_method(class_name) == expected


def test_get_props_stanzas(default_props_parser, get_props_stanza_results):
    default_props_parser.get_list_of_sources = MagicMock()
    default_props_parser.get_list_of_sources.side_effect = [
        ("*ta_snow_setup.log*1", "*ta_snow_setup.log*2"),
        ("*ta_snow_ticket.log*",),
    ]
    assert list(default_props_parser.get_props_stanzas()) == get_props_stanza_results


def test_get_props_stanzas_empty_props(props_parser_empty_conf):
    assert list(props_parser_empty_conf.get_props_stanzas()) == []


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
    pp = PropsProperty(NAME, "Value")
    assert len(list(default_props_parser.get_sourcetype_assignments(pp))) == 1
    field_mock.assert_called_once()
    field_mock.assert_called_with({"name": NAME, "expected_values": ["Value"]})


@pytest.mark.parametrize(
    "lookup_str, expected",
    [
        (
            f"{FIELD1} {FIELD2} {OUTPUTNEW} {FIELD3} {FIELD4} as {FIELD5}",
            {
                INPUT_FIELDS: [FIELD2],
                OUTPUT_FIELDS: [FIELD3, FIELD5],
                LOOKUP_STANZA: FIELD1,
            },
        ),
        (
            f"{FIELD1} {FIELD2} {FIELD3} {FIELD4} as {FIELD5}",
            {
                INPUT_FIELDS: [FIELD2, FIELD3, FIELD5],
                OUTPUT_FIELDS: [],
                LOOKUP_STANZA: FIELD1,
            },
        ),
        (
            f"{FIELD1} {FIELD2} {OUTPUT} {FIELD3} {FIELD4} as {FIELD5}",
            {
                INPUT_FIELDS: [FIELD2],
                OUTPUT_FIELDS: [FIELD3, FIELD5],
                LOOKUP_STANZA: FIELD1,
            },
        ),
        (
            f"{FIELD1} {FIELD2} {OUTPUTNEW} {FIELD3} {FIELD4} as {FIELD5} {FIELD6} as {FIELD7}",
            {
                INPUT_FIELDS: [FIELD2],
                OUTPUT_FIELDS: [FIELD3, FIELD5, FIELD7],
                LOOKUP_STANZA: FIELD1,
            },
        ),
        (
            f"{FIELD1} {FIELD2} {OUTPUTNEW} {FIELD3} {FIELD4} as {FIELD5} {OUTPUT} {FIELD6} as {FIELD7}",
            {
                INPUT_FIELDS: [FIELD2],
                OUTPUT_FIELDS: [FIELD7],
                LOOKUP_STANZA: FIELD1,
            },
        ),
    ],
)
def test_parse_lookup_str(default_props_parser, lookup_str, expected):
    default_props_parser.parse_lookup_str(lookup_str)


def test_get_report_fields(default_props_parser, transforms_parser, mocker):
    pp = PropsProperty(NAME, "Value, YYYYY,  AAAAAA GGGGG UUUUUUU , IIIIII")
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
        NAME,
        f"{FIELD1} {FIELD2} {OUTPUTNEW} {FIELD3} {FIELD4} as {FIELD5} {OUTPUT} {FIELD6} as {FIELD7}",
    )
    default_props_parser.parse_lookup_str = MagicMock(
        return_value={
            INPUT_FIELDS: [FIELD2],
            OUTPUT_FIELDS: [FIELD7],
            LOOKUP_STANZA: FIELD1,
        }
    )
    fields_list = default_props_parser.get_lookup_fields.__wrapped__(
        default_props_parser, pp
    )
    assert len(fields_list) == 2
    assert FIELD2 in fields_list
    assert FIELD7 in fields_list


def test_get_lookup_fields_no_output_fields(default_props_parser):
    pp = PropsProperty(NAME, f"{FIELD1} {FIELD2} {FIELD3} {FIELD4} as {FIELD5}")
    default_props_parser.parse_lookup_str = MagicMock(
        return_value={
            INPUT_FIELDS: [FIELD2, FIELD3, FIELD5],
            OUTPUT_FIELDS: [],
            LOOKUP_STANZA: FIELD1,
        }
    )
    default_props_parser.transforms_parser.get_lookup_csv_fields = MagicMock(
        return_value=("csv_field",)
    )
    fields_list = default_props_parser.get_lookup_fields.__wrapped__(
        default_props_parser, pp
    )
    assert len(fields_list) == 4
    assert FIELD2 in fields_list
    assert FIELD3 in fields_list
    assert FIELD5 in fields_list
    assert "csv_field" in fields_list


@pytest.mark.parametrize(
    "prop, expected",
    [
        (
            PropsProperty(
                NAME,
                f"{FIELD1} as {FIELD2} {FIELD8}",
            ),
            (FIELD1, FIELD2),
        ),
        (
            PropsProperty(
                NAME,
                f"{FIELD1} AS {FIELD2} {FIELD8}",
            ),
            (FIELD1, FIELD2),
        ),
        (
            PropsProperty(
                NAME,
                f"{FIELD1} ASNEW {FIELD2} {FIELD8} {FIELD5} asnew {FIELD6}",
            ),
            (FIELD1, FIELD2, FIELD5, FIELD6),
        ),
        (
            PropsProperty(
                NAME,
                f"{FIELD1} {FIELD2} ASNEW {OUTPUTNEW} {FIELD3} asnew fieldx {FIELD4} AS {FIELD5} {FIELD6} {FIELD7} as {FIELD8}",
            ),
            (
                FIELD2,
                OUTPUTNEW,
                FIELD3,
                "fieldx",
                FIELD4,
                FIELD5,
                FIELD7,
                FIELD8,
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
        (PropsProperty("key EVAL-val", f"EVAL-333 {FIELD1}"), ["val"]),
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


@pytest.mark.parametrize(
    "prop, expected",
    [
        (PropsProperty(NAME, "(?P<_KEY_df>the rest"), []),
        (PropsProperty(NAME, "(?<_VAL_df>the rest"), []),
        (PropsProperty(NAME, "(?<to_extract>the rest"), ["to_extract"]),
        (PropsProperty(NAME, "(?P'to_extract'the rest"), ["to_extract"]),
        (
            PropsProperty(NAME, f"(?P<to_extract>the rest In {FIELD1}  "),
            ["to_extract", FIELD1],
        ),
    ],
)
def test_get_extract_fields(default_props_parser, prop, expected):
    assert (
        list(
            default_props_parser.get_extract_fields.__wrapped__(
                default_props_parser, prop
            )
        )
        == expected
    )
