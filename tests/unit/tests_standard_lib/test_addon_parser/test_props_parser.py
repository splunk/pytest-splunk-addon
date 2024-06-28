import os

import pytest

from pytest_splunk_addon.addon_parser.props_parser import (
    PropsParser,
)
from pytest_splunk_addon.addon_parser.fields import Field


@pytest.fixture()
def default_props_parser() -> PropsParser:
    props_conf_path = os.path.join(os.path.dirname(__file__), "testdata")
    return PropsParser(props_conf_path)


@pytest.mark.parametrize(
    "src, expected",
    [
        ("source::...setup.log*", {"*setup.log*"}),
        ("source::...set...up.log*", {"*set*up.log*"}),
        ("source::...se_(tT)_a_(pP).log*", {"*se_tT_a_pP.log*"}),
        (
            "source::...s_(e|E)_t_(a|A)p.log*",
            {
                "*s_e_t_ap.log*",
                "*s_e_t_Ap.log*",
                "*s_E_t_ap.log*",
                "*s_E_t_Ap.log*",
            },
        ),
    ],
)
def test_get_list_of_sources(default_props_parser, src, expected):
    assert set(list(default_props_parser.get_list_of_sources(src))) == expected


def test_get_props_stanzas(default_props_parser):
    expected = [
        {
            "stanza": "sourcetype:test",
            "stanza_type": "sourcetype",
            "classname": "REPORT-field::fiction-tsc-regex-format",
            "fields": [
                Field({"name": "size1"}),
                Field({"name": "size2"}),
            ],
        },
        {
            "stanza": "sourcetype:test",
            "stanza_type": "sourcetype",
            "classname": "FIELDALIAS-fields",
            "fields": [
                Field({"name": "field_aliased_1"}),
                Field({"name": "field_2"}),
                Field({"name": "field_aliased_2"}),
                Field({"name": "field_1"}),
            ],
        },
        {
            "stanza": "sourcetype:test",
            "stanza_type": "sourcetype",
            "classname": "FIELDALIAS-fieldalias_1",
            "fields": [
                Field({"name": "field1"}),
                Field({"name": "field2"}),
            ],
        },
        {
            "stanza": "sourcetype:test",
            "stanza_type": "sourcetype",
            "classname": "FIELDALIAS-fieldalias_2",
            "fields": [
                Field({"name": "field1"}),
                Field({"name": "field2"}),
            ],
        },
        {
            "stanza": "sourcetype:test",
            "stanza_type": "sourcetype",
            "classname": "FIELDALIAS-fieldalias_3",
            "fields": [
                Field({"name": "field1"}),
                Field({"name": "field2"}),
                Field({"name": "field5"}),
                Field({"name": "field6"}),
            ],
        },
        {
            "stanza": "sourcetype:test",
            "stanza_type": "sourcetype",
            "classname": "FIELDALIAS-fieldalias_4",
            "fields": [
                Field({"name": "field2"}),
                Field({"name": "OUTPUTNEW"}),
                Field({"name": "field3"}),
                Field({"name": "fieldx"}),
                Field({"name": "field4"}),
                Field({"name": "field5"}),
                Field({"name": "field7"}),
                Field({"name": "field8"}),
            ],
        },
        {
            "stanza": "sourcetype:test",
            "stanza_type": "sourcetype",
            "classname": "LOOKUP-lookup_name_1",
            "fields": [
                Field({"name": "field2"}),
                Field({"name": "field3"}),
                Field({"name": "field5"}),
            ],
        },
        {
            "stanza": "sourcetype:test",
            "stanza_type": "sourcetype",
            "classname": "LOOKUP-lookup_name_2",
            "fields": [
                Field({"name": "field2"}),
                Field({"name": "field3"}),
                Field({"name": "field5"}),
            ],
        },
        {
            "stanza": "sourcetype:test",
            "stanza_type": "sourcetype",
            "classname": "LOOKUP-lookup_name_3",
            "fields": [
                Field({"name": "field2"}),
                Field({"name": "field3"}),
                Field({"name": "field5"}),
            ],
        },
        {
            "stanza": "sourcetype:test",
            "stanza_type": "sourcetype",
            "classname": "LOOKUP-lookup_name_4",
            "fields": [
                Field({"name": "field2"}),
                Field({"name": "field3"}),
                Field({"name": "field5"}),
                Field({"name": "field7"}),
            ],
        },
        {
            "stanza": "sourcetype:test",
            "stanza_type": "sourcetype",
            "classname": "LOOKUP-lookup_name_5",
            "fields": [
                Field({"name": "field2"}),
                Field({"name": "field7"}),
            ],
        },
        {
            "stanza": "sourcetype:test",
            "stanza_type": "sourcetype",
            "classname": "EXTRACT-extract_fields1",
            "fields": [
                Field({"name": "field1"}),
                Field({"name": "to_extract"}),
            ],
        },
        {
            "stanza": "sourcetype:test",
            "stanza_type": "sourcetype",
            "classname": "EXTRACT-extract_fields2",
            "fields": [
                Field({"name": "to_extract"}),
            ],
        },
        {
            "stanza": "sourcetype:test",
            "stanza_type": "sourcetype",
            "classname": "EXTRACT-extract_fields3",
            "fields": [
                Field({"name": "to_extract"}),
            ],
        },
    ]
    result = list(default_props_parser.get_props_fields())
    for i, r in enumerate(result[: len(expected)]):
        assert expected[i]["stanza"] == r["stanza"]
        assert expected[i]["stanza_type"] == r["stanza_type"]
        assert expected[i]["classname"] == r["classname"]
        assert sorted(expected[i]["fields"]) == sorted(r["fields"])


def test_get_props_stanzas_no_fields_for_key_val_extractions(default_props_parser):
    expected_classnames_without_extractions = [
        "EXTRACT-extract_fields4",
        "EXTRACT-extract_fields5",
    ]
    result = list(default_props_parser.get_props_fields())
    for elem in result:
        assert elem["classname"] not in expected_classnames_without_extractions


def test_get_props_method_unknown_classname(default_props_parser):
    unknown_classname = "UNKNOWN_CLASS_NAME-key"
    result = list(default_props_parser.get_props_fields())
    for elem in result:
        assert elem["classname"] != unknown_classname


def test_no_props_config_file():
    props_parser = PropsParser("unused_path")
    assert props_parser.props is None
