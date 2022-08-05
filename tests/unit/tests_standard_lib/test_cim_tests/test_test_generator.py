import pytest
from unittest.mock import patch, MagicMock
from collections import namedtuple
from pytest_splunk_addon.standard_lib.cim_tests.test_generator import CIMTestGenerator

field = namedtuple("Field", ["type", "name"], defaults=["", ""])
data_set = namedtuple("DataSet", ["fields", "fields_cluster"])

TEST_TYPES = ["indextime", "modinput", "knowledge"]
FIELDS = [
    field(type="knowledge", name="knowledge_field"),
    field(type="cim", name="cim_field"),
    field(type="modinput", name="modinput_field"),
]
NOT_ALLOWED_FIELDS = [
    field(type="not_allowed_in_search_and_props", name="field_props_and_search_na"),
    field(type="not_allowed_in_props", name="field_props_na"),
    field(type="not_allowed_in_search_and_props", name="field_not_allowed"),
]


@pytest.fixture()
def mocked_cim_test_generator():
    with patch.object(CIMTestGenerator, "__init__", return_value=None):
        return CIMTestGenerator()


@pytest.fixture()
def field_mock(monkeypatch):
    field = MagicMock()
    monkeypatch.setattr(
        "pytest_splunk_addon.standard_lib.cim_tests.test_generator.Field", field
    )
    return field


@pytest.fixture()
def mapped_datasets():
    return [
        (
            'eventtype="eventtype_splunkd_fiction_one"',
            [data_set(fields=FIELDS[:], fields_cluster=[FIELDS[:]])],
        ),
    ]


@pytest.fixture()
def fake_addon_parser():
    event_types = [
        {"stanza": "fiction_is_splunkd"},
        {"stanza": "fiction_for_tags_positive"},
        {"stanza": "fiction_is_splunkd-%host%"},
    ]
    props_fields = [
        {
            "stanza": "eventtype_splunkd_fiction_one",
            "fields": [FIELDS[0], NOT_ALLOWED_FIELDS[0]],
            "classname": "invalid_fields",
        },
        {
            "stanza": "eventtype_splunkd_fiction_two",
            "fields": [NOT_ALLOWED_FIELDS[1], FIELDS[1], NOT_ALLOWED_FIELDS[2]],
            "classname": "broken_tests",
        },
    ]
    ap = MagicMock()
    ap.get_eventtypes.side_effect = lambda: (event for event in event_types)
    ap.get_props_fields.side_effect = lambda: (ps for ps in props_fields)
    return ap


@pytest.mark.parametrize(
    "args",
    [
        (
            "addon_path",
            "data_model_path",
            [],
        ),
        (
            "addon_path",
            "data_model_path",
            [],
            ["optional"],
            "fake_common_fields_path",
        ),
    ],
)
def test_cim_test_generator_instantiation(args):
    with patch(
        "pytest_splunk_addon.standard_lib.cim_tests.test_generator.DataModelHandler",
        return_value="DATA_MODEL_HANDLER_RETURN_VALUE",
    ) as dtm_mock, patch(
        "pytest_splunk_addon.standard_lib.cim_tests.test_generator.AddonParser",
        return_value="ADDON_PARSER_RETURN_VALUE",
    ) as ap_mock:
        cim = CIMTestGenerator(*args)
        assert cim.data_model_handler == "DATA_MODEL_HANDLER_RETURN_VALUE"
        assert cim.addon_parser == "ADDON_PARSER_RETURN_VALUE"
        dtm_mock.assert_called_once_with("data_model_path")
        ap_mock.assert_called_once_with("addon_path")
        if len(args) == 3:
            assert cim.test_field_type == ["required", "conditional"]
            assert (
                "pytest_splunk_addon/standard_lib/cim_tests/CommonFields.json"
                in cim.common_fields_path
            )
        else:
            assert cim.test_field_type == args[3]
            assert cim.common_fields_path == args[4]


@pytest.mark.parametrize(
    "fixture_name, expected_ouptput",
    [
        ("splunk_searchtime_cim_fields", "GENERATE_CIM_FILED_TESTS_RETURN_VALUE"),
        (
            "splunk_searchtime_cim_fields_not_allowed_in_props",
            "GENERATE_FILED_EXTRACTIONS_TEST_RETURN_VALUE",
        ),
        (
            "splunk_searchtime_cim_fields_not_allowed_in_search",
            "GENERATE_FILEDS_EVENT_COUNT_TEST_RETURN_VALUE",
        ),
        (
            "splunk_searchtime_cim_mapped_datamodel",
            "GENERATE_MAPPED_DATAMODEL_TESTS_RETURN_VALUE",
        ),
    ],
)
def test_generate_tests(mocked_cim_test_generator, fixture_name, expected_ouptput):
    with patch.object(
        CIMTestGenerator,
        "generate_cim_fields_tests",
        return_value=(["GENERATE_CIM_FILED_TESTS_RETURN_VALUE"]),
    ), patch.object(
        CIMTestGenerator,
        "generate_field_extractions_test",
        return_value=(["GENERATE_FILED_EXTRACTIONS_TEST_RETURN_VALUE"]),
    ), patch.object(
        CIMTestGenerator,
        "generate_fields_event_count_test",
        return_value=(["GENERATE_FILEDS_EVENT_COUNT_TEST_RETURN_VALUE"]),
    ), patch.object(
        CIMTestGenerator,
        "generate_mapped_datamodel_tests",
        return_value=(["GENERATE_MAPPED_DATAMODEL_TESTS_RETURN_VALUE"]),
    ):
        assert list(mocked_cim_test_generator.generate_tests(fixture_name)) == [
            expected_ouptput
        ]


def test_get_mapped_datasets(mocked_cim_test_generator):
    dth = MagicMock()
    dth.get_mapped_data_models.side_effect = lambda x: (
        f"data_model_{i}" for i in range(3)
    )
    mocked_cim_test_generator.data_model_handler = dth
    mocked_cim_test_generator.addon_parser = "fake_addon_parser"
    assert list(mocked_cim_test_generator.get_mapped_datasets()) == [
        "data_model_0",
        "data_model_1",
        "data_model_2",
    ]
    dth.get_mapped_data_models.assert_called_once_with("fake_addon_parser")


def test_generate_cim_fields_tests(mocked_cim_test_generator, mapped_datasets):
    mocked_cim_test_generator.test_field_type = TEST_TYPES
    data_set_list = mapped_datasets[0][1]
    stanza = mapped_datasets[0][0]
    with patch.object(
        CIMTestGenerator, "get_mapped_datasets", return_value=mapped_datasets
    ), patch.object(pytest, "param", side_effect=lambda x, id: (x, id)) as param_mock:
        assert list(mocked_cim_test_generator.generate_cim_fields_tests()) == [
            (
                {"tag_stanza": stanza, "data_set": data_set_list, "fields": []},
                f"{stanza}::{data_set_list[0]}",
            ),
            (
                {
                    "tag_stanza": stanza,
                    "data_set": data_set_list,
                    "fields": [FIELDS[0]],
                },
                f"{stanza}::{data_set_list[0]}::{FIELDS[0]}",
            ),
            (
                {
                    "tag_stanza": stanza,
                    "data_set": data_set_list,
                    "fields": [FIELDS[2]],
                },
                f"{stanza}::{data_set_list[0]}::{FIELDS[2]}",
            ),
            (
                {
                    "tag_stanza": stanza,
                    "data_set": data_set_list,
                    "fields": FIELDS,
                },
                f"{stanza}::{data_set_list[0]}::knowledge_field+cim_field+modinput_field",
            ),
        ]
        assert param_mock.call_count == 4


def test_generate_field_extractions_test(
    mocked_cim_test_generator, mapped_datasets, fake_addon_parser
):
    mocked_cim_test_generator.addon_parser = fake_addon_parser
    mapped_datasets[0][1][0].fields.extend(NOT_ALLOWED_FIELDS[1:])
    with patch.object(
        CIMTestGenerator, "get_common_fields", return_value=NOT_ALLOWED_FIELDS[:2]
    ), patch.object(
        CIMTestGenerator,
        "get_mapped_datasets",
        side_effect=lambda: (dataset for dataset in mapped_datasets),
    ), patch.object(
        pytest, "param", side_effect=lambda x, id: (x, id)
    ) as param_mock:
        assert list(mocked_cim_test_generator.generate_field_extractions_test()) == [
            (
                {
                    "fields": [
                        {
                            "name": NOT_ALLOWED_FIELDS[0].name,
                            "stanza": "eventtype_splunkd_fiction_one",
                            "classname": "invalid_fields",
                        },
                        {
                            "name": NOT_ALLOWED_FIELDS[1].name,
                            "stanza": "eventtype_splunkd_fiction_two",
                            "classname": "broken_tests",
                        },
                        {
                            "name": NOT_ALLOWED_FIELDS[2].name,
                            "stanza": "eventtype_splunkd_fiction_two",
                            "classname": "broken_tests",
                        },
                    ]
                },
                f"searchtime_cim_fields",
            )
        ]
        param_mock.assert_called_once()


def test_generate_fields_event_count_test(mocked_cim_test_generator, mapped_datasets):
    mapped_datasets.extend(
        [
            (
                'eventtype="empty_stanza"',
                [data_set(fields=[], fields_cluster=[])],
            ),
            (
                'eventtype="not_allowed_stanza"',
                [data_set(fields=NOT_ALLOWED_FIELDS, fields_cluster=[])],
            ),
        ]
    )
    data_set_list = [mapped_datasets[0][1], mapped_datasets[2][1]]
    stanza = [mapped_datasets[0][0], mapped_datasets[2][0]]
    with patch.object(
        CIMTestGenerator, "get_common_fields", return_value=NOT_ALLOWED_FIELDS[:2]
    ), patch.object(
        CIMTestGenerator,
        "get_mapped_datasets",
        side_effect=lambda: (dataset for dataset in mapped_datasets),
    ), patch.object(
        pytest, "param", side_effect=lambda x, id: (x, id)
    ) as param_mock:
        out = list(mocked_cim_test_generator.generate_fields_event_count_test())
        assert out == [
            (
                {
                    "tag_stanza": stanza[0],
                    "data_set": data_set_list[0],
                    "fields": NOT_ALLOWED_FIELDS[:2],
                },
                f"{stanza[0]}::{data_set_list[0][0]}",
            ),
            (
                {
                    "tag_stanza": stanza[1],
                    "data_set": data_set_list[1],
                    "fields": NOT_ALLOWED_FIELDS,
                },
                f"{stanza[1]}::{data_set_list[1][0]}",
            ),
        ]
        assert param_mock.call_count == 2


@pytest.mark.parametrize(
    "args, expected_output", [((TEST_TYPES,), [FIELDS[0], FIELDS[2]]), (tuple(), [])]
)
def test_get_common_fields(
    open_mock,
    json_load_mock,
    field_mock,
    mocked_cim_test_generator,
    args,
    expected_output,
):
    json_load_mock.return_value = {"fields": FIELDS}
    field_mock.parse_fields.side_effect = lambda x: x
    mocked_cim_test_generator.common_fields_path = "fake_path"
    assert mocked_cim_test_generator.get_common_fields(*args) == expected_output
    field_mock.parse_fields.assert_called_once_with(FIELDS)
    open_mock.assert_called_once_with("fake_path", "r")


def test_generate_mapped_datamodel_tests(mocked_cim_test_generator, fake_addon_parser):
    mocked_cim_test_generator.addon_parser = fake_addon_parser
    with patch.object(
        pytest, "param", return_value="PYTEST_PARAM_RETURN_VALUE"
    ) as param_mock:
        assert list(mocked_cim_test_generator.generate_mapped_datamodel_tests()) == [
            "PYTEST_PARAM_RETURN_VALUE"
        ]
        param_mock.assert_called_once_with(
            {
                "eventtypes": [
                    "fiction_is_splunkd",
                    "fiction_for_tags_positive",
                    "fiction_is_splunkd-%host%",
                ]
            },
            id="mapped_datamodel_tests",
        )
