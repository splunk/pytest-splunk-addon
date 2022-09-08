import pytest
from unittest.mock import patch, MagicMock
from pytest_splunk_addon.standard_lib.fields_tests.test_generator import (
    FieldTestGenerator,
)


def field_1():
    pass


def field_2():
    pass


def field_3():
    pass


field_1.__dict__.update({"name": "field_1"})
field_2.__dict__.update({"name": "field_2"})
field_3.__dict__.update({"name": "field_3"})


@pytest.fixture()
def addon_parser_mock(monkeypatch):
    ap = MagicMock()
    ap.return_value = ap
    monkeypatch.setattr(
        "pytest_splunk_addon.standard_lib.fields_tests.test_generator.AddonParser", ap
    )
    return ap


@pytest.fixture()
def field_bank_mock(monkeypatch):
    fb = MagicMock()
    monkeypatch.setattr(
        "pytest_splunk_addon.standard_lib.fields_tests.test_generator.FieldBank", fb
    )
    return fb


def test_field_test_generator_instantiation(addon_parser_mock):
    addon_parser_mock.return_value = "ADDON_PARSER_RETURN_VALUE"
    ftg = FieldTestGenerator(
        "app_path",
        [],
        "field_bank",
    )
    assert ftg.field_bank == "field_bank"
    assert ftg.addon_parser == "ADDON_PARSER_RETURN_VALUE"
    addon_parser_mock.assert_called_once_with("app_path")


@pytest.mark.parametrize(
    "fixture_name, expected_ouptput",
    [
        ("splunk_searchtime_fields_positive", "GENERATE_FILED_TESTS_RETURN_VALUE"),
        (
            "splunk_searchtime_fields_negative",
            "GENERATE_FILED_TESTS_RETURN_VALUE",
        ),
        (
            "splunk_searchtime_fields_tags",
            "GENERATE_TAG_TESTS_RETURN_VALUE",
        ),
        (
            "splunk_searchtime_fields_eventtypes",
            "GENERATE_EVENTTYPE_TESTS_RETURN_VALUE",
        ),
        (
            "splunk_searchtime_fields_savedsearches",
            "GENERATE_SAVEDSEARCHES_TESTS_RETURN_VALUE",
        ),
    ],
)
def test_generate_tests(addon_parser_mock, fixture_name, expected_ouptput):
    with patch.object(
        FieldTestGenerator,
        "generate_field_tests",
        return_value=(["GENERATE_FILED_TESTS_RETURN_VALUE"]),
    ), patch.object(
        FieldTestGenerator,
        "generate_tag_tests",
        return_value=(["GENERATE_TAG_TESTS_RETURN_VALUE"]),
    ), patch.object(
        FieldTestGenerator,
        "generate_eventtype_tests",
        return_value=(["GENERATE_EVENTTYPE_TESTS_RETURN_VALUE"]),
    ), patch.object(
        FieldTestGenerator,
        "generate_savedsearches_tests",
        return_value=(["GENERATE_SAVEDSEARCHES_TESTS_RETURN_VALUE"]),
    ):
        assert list(
            FieldTestGenerator(
                "app_path",
                [],
                "field_bank",
            ).generate_tests(fixture_name)
        ) == [expected_ouptput]


def test_generate_tag_tests(addon_parser_mock):
    tags = [
        {
            "stanza": 'eventtype="fiction_for_tags_positive"',
            "tag": "tags_positive_event",
            "enabled": True,
        },
        {
            "stanza": 'source="/opt/splunk/var/log/splunk/splunkd.log"',
            "tag": "tags_disabled_event",
            "enabled": False,
        },
    ]
    addon_parser_mock.get_tags.side_effect = lambda: (tag for tag in tags)
    with patch.object(pytest, "param", side_effect=lambda x, id: (x, id)) as param_mock:
        out = list(
            FieldTestGenerator(
                "app_path",
                [],
                "field_bank",
            ).generate_tag_tests()
        )
        assert out == [
            (tags[0], f"{tags[0]['stanza']}::tag::{tags[0]['tag']}"),
            (tags[1], f"{tags[1]['stanza']}::tag::{tags[1]['tag']}"),
        ]
        assert param_mock.call_count == len(tags)


def test_generate_eventtype_tests(addon_parser_mock):
    eventtypes = [
        {"stanza": "fiction_is_splunkd"},
        {"stanza": "fiction_for_tags_positive"},
        {"stanza": "fiction_is_splunkd-%host%"},
    ]
    addon_parser_mock.get_eventtypes.side_effect = lambda: (
        event for event in eventtypes
    )
    with patch.object(pytest, "param", side_effect=lambda x, id: (x, id)) as param_mock:
        out = list(
            FieldTestGenerator(
                "app_path",
                [],
                "field_bank",
            ).generate_eventtype_tests()
        )
        assert out == [
            (eventtypes[0], f"eventtype::{eventtypes[0]['stanza']}"),
            (eventtypes[1], f"eventtype::{eventtypes[1]['stanza']}"),
            (eventtypes[2], f"eventtype::{eventtypes[2]['stanza']}"),
        ]
        assert param_mock.call_count == len(eventtypes)


def test_generate_savedsearches_tests(addon_parser_mock):
    savedsearches = [
        {
            "stanza": "basic_search",
            "search": "index = _internal | stats count by sourcetype",
        },
        {"stanza": "empty_search", "search": 'index = "main"'},
    ]
    addon_parser_mock.get_savedsearches.side_effect = lambda: (
        savedsearch for savedsearch in savedsearches
    )
    with patch.object(pytest, "param", side_effect=lambda x, id: (x, id)) as param_mock:
        out = list(
            FieldTestGenerator(
                "app_path",
                [],
                "field_bank",
            ).generate_savedsearches_tests()
        )
        assert out == [
            (savedsearches[0], savedsearches[0]["stanza"]),
            (savedsearches[1], savedsearches[1]["stanza"]),
        ]
        assert param_mock.call_count == len(savedsearches)


@pytest.mark.parametrize(
    "fields_group, criteria, expected_result",
    [
        ({"classname": "valid_classname"}, ["valid_class", "valid_classname"], True),
        ({"classname": "invalid_classname"}, ["valid_class", "valid_classname"], False),
    ],
)
def test_contains_classname(fields_group, criteria, expected_result):
    assert (
        FieldTestGenerator(
            "app_path",
            [],
            "field_bank",
        )._contains_classname(fields_group, criteria)
        is expected_result
    )


@pytest.mark.parametrize(
    "is_positive, contains_classname, field_bank, prpos_fields, expected_output",
    [
        (
            False,
            [False, False],
            [
                {
                    "stanza": "sourcetype::splunkd",
                    "stanza_type": "sourcetype",
                    "classname": "field_bank",
                    "fields": [field_2, field_3],
                }
            ],
            [
                {
                    "stanza": "snow:incident",
                    "stanza_type": "sourcetype",
                    "classname": "REPORT::transform_string",
                    "fields": [field_1],
                }
            ],
            [
                (
                    {
                        "stanza": "sourcetype::splunkd",
                        "stanza_type": "sourcetype",
                        "classname": "field_bank",
                        "fields": [{"name": "field_2"}],
                    },
                    f"sourcetype::splunkd::field_bank_1::{field_2}",
                ),
                (
                    {
                        "stanza": "sourcetype::splunkd",
                        "stanza_type": "sourcetype",
                        "classname": "field_bank",
                        "fields": [{"name": "field_3"}],
                    },
                    f"sourcetype::splunkd::field_bank_2::{field_3}",
                ),
                (
                    {
                        "stanza": "snow:incident",
                        "stanza_type": "sourcetype",
                        "classname": "REPORT::transform_string",
                        "fields": [{"name": "field_1"}],
                    },
                    f"snow:incident::field::{field_1}",
                ),
            ],
        ),
        (
            True,
            [False, False],
            [
                {
                    "stanza": "sourcetype::splunkd",
                    "stanza_type": "sourcetype",
                    "classname": "field_bank",
                    "fields": [field_2],
                }
            ],
            [
                {
                    "stanza": "snow:incident",
                    "stanza_type": "sourcetype",
                    "classname": "REPORT::transform_string",
                    "fields": [field_1],
                }
            ],
            [
                (
                    {
                        "stanza": "sourcetype::splunkd",
                        "stanza_type": "sourcetype",
                        "classname": "field_bank",
                        "fields": [],
                    },
                    "sourcetype::splunkd",
                ),
                (
                    {
                        "stanza": "sourcetype::splunkd",
                        "stanza_type": "sourcetype",
                        "classname": "field_bank",
                        "fields": [{"name": "field_2"}],
                    },
                    f"sourcetype::splunkd::field_bank_1::{field_2}",
                ),
                (
                    {
                        "stanza": "snow:incident",
                        "stanza_type": "sourcetype",
                        "classname": "REPORT::transform_string",
                        "fields": [],
                    },
                    "snow:incident",
                ),
                (
                    {
                        "stanza": "snow:incident",
                        "stanza_type": "sourcetype",
                        "classname": "REPORT::transform_string",
                        "fields": [{"name": "field_1"}],
                    },
                    f"snow:incident::field::{field_1}",
                ),
            ],
        ),
        (
            False,
            [False, True],
            [
                {
                    "stanza": "sourcetype::splunkd",
                    "stanza_type": "sourcetype",
                    "classname": "field_bank",
                    "fields": [field_2],
                }
            ],
            [
                {
                    "stanza": "snow:incident",
                    "stanza_type": "sourcetype",
                    "classname": "REPORT::transform_string",
                    "fields": [field_1, field_3],
                }
            ],
            [
                (
                    {
                        "stanza": "sourcetype::splunkd",
                        "stanza_type": "sourcetype",
                        "classname": "field_bank",
                        "fields": [{"name": "field_2"}],
                    },
                    f"sourcetype::splunkd::field_bank_1::{field_2}",
                ),
                (
                    {
                        "stanza": "snow:incident",
                        "stanza_type": "sourcetype",
                        "classname": "REPORT::transform_string",
                        "fields": [{"name": "field_1"}, {"name": "field_3"}],
                    },
                    "snow:incident::REPORT::transform_string",
                ),
                (
                    {
                        "stanza": "snow:incident",
                        "stanza_type": "sourcetype",
                        "classname": "REPORT::transform_string",
                        "fields": [{"name": "field_1"}],
                    },
                    f"snow:incident::field::{field_1}",
                ),
                (
                    {
                        "stanza": "snow:incident",
                        "stanza_type": "sourcetype",
                        "classname": "REPORT::transform_string",
                        "fields": [{"name": "field_3"}],
                    },
                    f"snow:incident::field::{field_3}",
                ),
            ],
        ),
    ],
)
def test_generate_field_tests(
    addon_parser_mock,
    field_bank_mock,
    is_positive,
    contains_classname,
    field_bank,
    prpos_fields,
    expected_output,
):
    addon_parser_mock.get_props_fields.return_value = prpos_fields
    field_bank_mock.init_field_bank_tests.return_value = field_bank
    with patch.object(
        FieldTestGenerator, "_contains_classname", side_effect=contains_classname
    ), patch.object(pytest, "param", side_effect=lambda x, id: (x, id)) as param_mock:
        out = list(
            FieldTestGenerator(
                "app_path",
                [],
                "field_bank",
            ).generate_field_tests(is_positive)
        )
        assert out == expected_output
        assert param_mock.call_count == len(expected_output)
