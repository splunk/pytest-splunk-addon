import pytest
from unittest.mock import patch, MagicMock
from pytest_splunk_addon.standard_lib.cim_tests.test_generator import CIMTestGenerator


@pytest.fixture()
def mocked_cim_test_generator():
    with patch.object(CIMTestGenerator, "__init__", return_value=None):
        return CIMTestGenerator()


@pytest.mark.parametrize(
    "args",
    [
        ("addon_path", "data_model_path"),
        ("addon_path", "data_model_path", ["optional"], "fake_common_fields_path"),
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
        if len(args) == 2:
            assert cim.test_field_type == ["required", "conditional"]
            assert (
                "pytest_splunk_addon/standard_lib/cim_tests/CommonFields.json"
                in cim.common_fields_path
            )
        else:
            assert cim.test_field_type == args[2]
            assert cim.common_fields_path == args[3]


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
