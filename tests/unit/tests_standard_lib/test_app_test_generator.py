import pytest
from unittest.mock import patch
from collections import namedtuple
from pytest_splunk_addon.standard_lib.app_test_generator import AppTestGenerator

module = "pytest_splunk_addon.standard_lib.app_test_generator"
config = {
    "splunk_app": "fake_app",
    "field_bank": "fake_field_bank",
    "splunk_dm_path": "fake_path",
    "store_events": True,
    "splunk_data_generator": "psa.conf",
    "requirement_test": "fake_requirement_path",
}
pytest_config = namedtuple("Config", ["getoption"])
test_config = pytest_config(getoption=lambda x, *y: config[x])
test_config_without_dm_path = pytest_config(
    getoption=lambda x, *y: config[x] if x != "splunk_dm_path" else None
)
params = namedtuple("ParameterSet", ["values", "id"])


@pytest.fixture()
def app_test_generator(mock_object):
    fieldtest_generator = mock_object(f"{module}.FieldTestGenerator")
    cim_test_generator = mock_object(f"{module}.CIMTestGenerator")
    indextime_test_generator = mock_object(f"{module}.IndexTimeTestGenerator")
    requirement_test_generator = mock_object(f"{module}.ReqsTestGenerator")
    for mock_element in [
        fieldtest_generator,
        cim_test_generator,
        indextime_test_generator,
        requirement_test_generator,
    ]:
        setattr(mock_element, "return_value", mock_element)


@pytest.mark.parametrize(
    "simple_config, path",
    [
        (test_config, "fake_path"),
        (test_config_without_dm_path, "/fake_dir/data_models"),
    ],
)
def test_app_test_generator_instantiation(
    mock_object, os_path_join_file_mock, app_test_generator, simple_config, path
):
    os_path_dirname_mock = mock_object("os.path.dirname")
    os_path_dirname_mock.return_value = "/fake_dir"
    atg = AppTestGenerator(simple_config)
    atg.fieldtest_generator.assert_called_once_with(
        config["splunk_app"], field_bank=config["field_bank"]
    )
    atg.cim_test_generator.assert_called_once_with(config["splunk_app"], path)
    atg.requirement_test_generator.assert_called_once_with(config["requirement_test"])
    atg.indextime_test_generator.assert_called_once_with()


@pytest.mark.parametrize(
    "fixture, called_function, test_generator, generator_args, generator_kwargs, expected_tests, dedup_call_count",
    [
        (
            "splunk_searchtime_fields",
            "fieldtest_generator",
            lambda fixture: (f"{fixture}_test_{i + 1}" for i in range(3)),
            ["splunk_searchtime_fields"],
            {},
            [
                "splunk_searchtime_fields_test_1",
                "splunk_searchtime_fields_test_2",
                "splunk_searchtime_fields_test_3",
            ],
            1,
        ),
        (
            "splunk_searchtime_cim",
            "cim_test_generator",
            lambda fixture: (f"{fixture}_test_{i + 1}" for i in range(3)),
            ["splunk_searchtime_cim"],
            {},
            [
                "splunk_searchtime_cim_test_1",
                "splunk_searchtime_cim_test_2",
                "splunk_searchtime_cim_test_3",
            ],
            1,
        ),
        (
            "splunk_searchtime_requirement",
            "requirement_test_generator",
            lambda fixture: (f"{fixture}_test_{i + 1}" for i in range(3)),
            ["splunk_searchtime_requirement"],
            {},
            [
                "splunk_searchtime_requirement_test_1",
                "splunk_searchtime_requirement_test_2",
                "splunk_searchtime_requirement_test_3",
            ],
            1,
        ),
        (
            "splunk_indextime_key_fields",
            "indextime_test_generator",
            lambda x, app_path, config_path, test_type: (
                params(values=f"splunk_indextime_{test_type}_test_{3 - i}", id=3 - i)
                for i in range(3)
            ),
            [True],
            {
                "app_path": "fake_app",
                "config_path": "psa.conf",
                "test_type": "key_fields",
            },
            [
                params(values=f"splunk_indextime_key_fields_test_1", id=1),
                params(values=f"splunk_indextime_key_fields_test_2", id=2),
                params(values=f"splunk_indextime_key_fields_test_3", id=3),
            ],
            0,
        ),
        (
            "splunk_indextime_time",
            "indextime_test_generator",
            lambda x, app_path, config_path, test_type: (
                params(values=f"splunk_indextime_{test_type}_test_{3 - i}", id=3 - i)
                for i in range(3)
            ),
            [True],
            {"app_path": "fake_app", "config_path": "psa.conf", "test_type": "_time"},
            [
                params(values=f"splunk_indextime__time_test_1", id=1),
                params(values=f"splunk_indextime__time_test_2", id=2),
                params(values=f"splunk_indextime__time_test_3", id=3),
            ],
            0,
        ),
        (
            "splunk_indextime_line_breaker",
            "indextime_test_generator",
            lambda x, app_path, config_path, test_type: (
                params(values=f"splunk_indextime_{test_type}_test_{3 - i}", id=3 - i)
                for i in range(3)
            ),
            [True],
            {
                "app_path": "fake_app",
                "config_path": "psa.conf",
                "test_type": "line_breaker",
            },
            [
                params(values=f"splunk_indextime_line_breaker_test_1", id=1),
                params(values=f"splunk_indextime_line_breaker_test_2", id=2),
                params(values=f"splunk_indextime_line_breaker_test_3", id=3),
            ],
            0,
        ),
    ],
)
def test_generate_tests(
    app_test_generator,
    fixture,
    called_function,
    test_generator,
    generator_args,
    generator_kwargs,
    expected_tests,
    dedup_call_count,
):
    atg = AppTestGenerator(test_config)
    setattr(getattr(atg, called_function).generate_tests, "side_effect", test_generator)
    with patch.object(
        AppTestGenerator, "dedup_tests", side_effect=lambda x, y: x
    ) as dedup_mock:
        out = list(atg.generate_tests(fixture))
        assert out == expected_tests
        getattr(atg, called_function).generate_tests.assert_called_once_with(
            *generator_args, **generator_kwargs
        )
        assert dedup_mock.call_count == dedup_call_count


def test_dedup_tests(app_test_generator):
    parameter_list = [params(values=f"val{x}", id=x) for x in range(7)]
    atg = AppTestGenerator(test_config)
    out = []
    for parameters in [parameter_list[:3], parameter_list[2:5]]:
        out.extend(atg.dedup_tests(parameters, "splunk_searchtime"))
    assert out == parameter_list[:5]
    assert atg.seen_tests == {("splunk_searchtime", x) for x in range(5)}
