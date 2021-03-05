import pytest
from unittest.mock import MagicMock, patch, call
from collections import namedtuple
from pytest_splunk_addon.standard_lib.utilities.junit_parser import JunitParser, main

testcase = namedtuple("TestCase", ["name", "result"])
prop = namedtuple("Property", ["name", "value"])
result_pass = MagicMock(_tag="pass")
result_failure = MagicMock(_tag="failure", message="test error message")
result_skipped = MagicMock(_tag="skipped")


@pytest.fixture()
def junit_xml_mock(monkeypatch):
    jux = MagicMock()
    monkeypatch.setattr(
        "pytest_splunk_addon.standard_lib.utilities.junit_parser.JUnitXml", jux
    )
    return jux


@pytest.fixture()
def junit_parser():
    with patch.object(JunitParser, "__init__", return_value=None):
        return JunitParser()


@pytest.fixture()
def os_path_mock(monkeypatch):
    os = MagicMock()
    monkeypatch.setattr("os.path", os)
    return os


@pytest.fixture()
def cim_report_generator_mock(monkeypatch):
    crg = MagicMock()
    crg.return_value = crg
    monkeypatch.setattr(
        "pytest_splunk_addon.standard_lib.utilities.junit_parser.CIMReportGenerator",
        crg,
    )
    return crg


@pytest.fixture()
def argparse_mock(monkeypatch):
    ap = MagicMock()
    ap.return_value = ap
    monkeypatch.setattr("argparse.ArgumentParser", ap)
    return ap


@pytest.fixture()
def junit_parser_mock(monkeypatch):
    jup = MagicMock()
    jup.return_value = jup
    monkeypatch.setattr(
        "pytest_splunk_addon.standard_lib.utilities.junit_parser.JunitParser", jup
    )
    return jup


@pytest.fixture()
def sys_exit_mock(monkeypatch):
    sys = MagicMock()
    sys.return_value = sys
    monkeypatch.setattr("sys.exit", sys)
    return sys


def test_junit_parser_instantiation(junit_xml_mock, os_path_mock):
    os_path_mock.isfile.return_value = True
    junit_xml_mock.fromfile.return_value = "JUnit Xml from file return value"
    jup = JunitParser("fake_path")
    assert jup._xml == "JUnit Xml from file return value"


@pytest.mark.parametrize(
    "multiple_xml, expected_error, error_message",
    [
        (
            True,
            Exception,
            "Generating Report for multiple xml is not currently Supported.",
        ),
        (
            False,
            FileNotFoundError,
            "\\[Errno 2\\] No such file or directory: 'fake_path'",
        ),
    ],
)
def test_junit_parser_instantiation_exception(
    os_path_mock, multiple_xml, expected_error, error_message
):
    os_path_mock.isfile.return_value = False
    os_path_mock.isdir.return_value = multiple_xml
    with pytest.raises(expected_error, match=error_message):
        JunitParser("fake_path")


def test_parse_junit(junit_parser):
    junit_parser._xml = [
        [
            testcase(name="test_cim_required_fields", result=result_pass),
            testcase(name="test_cim_required_fields", result=None),
        ],
        [
            testcase(name="test_cim_required_fields", result=result_failure),
            testcase(name="test_no_cim_required_fields", result=result_failure),
            testcase(name="test_cim_required_fields", result=result_skipped),
        ],
    ]
    with patch.object(
        JunitParser,
        "get_properties",
        lambda x, tc: f'{tc.name}::{tc.result._tag if hasattr(tc.result, "_tag") else "no_result"}',
    ):
        junit_parser.parse_junit()
    assert junit_parser.data == [
        "test_cim_required_fields::no_result",
        "test_cim_required_fields::failure",
        "test_cim_required_fields::skipped",
    ]


@pytest.mark.parametrize(
    "tc_name, tc_result, expected_output",
    [
        (
            "cim",
            None,
            {
                "status": "passed",
                "test_property": "-",
                "data_model": "cim_data_model",
                "data_set": "cim_data_set",
                "fields": "cim_fields",
                "tag_stanza": "cim_tag_stanza",
                "fields_type": "cim_fields_type",
            },
        ),
        (
            "fields",
            result_failure,
            {
                "status": "failed",
                "test_property": "test error message",
                "data_model": "fields_data_model",
                "data_set": "fields_data_set",
                "fields": "fields_fields",
                "tag_stanza": "fields_tag_stanza",
                "fields_type": "fields_fields_type",
            },
        ),
        (
            "index",
            result_skipped,
            {
                "status": "skipped",
                "test_property": "-",
                "data_model": "index_data_model",
                "data_set": "index_data_set",
                "fields": "index_fields",
                "tag_stanza": "index_tag_stanza",
                "fields_type": "index_fields_type",
            },
        ),
    ],
)
def test_get_properties(junit_parser, tc_name, tc_result, expected_output):
    with patch.object(
        JunitParser,
        "yield_properties",
        lambda x, tc: [
            prop(name="data_model", value=f"{tc.name}_data_model"),
            prop(name="data_set", value=f"{tc.name}_data_set"),
            prop(name="fields", value=f"{tc.name}_fields"),
            prop(name="tag_stanza", value=f"{tc.name}_tag_stanza"),
            prop(name="fields_type", value=f"{tc.name}_fields_type"),
            prop(name="fake_prop", value=f"{tc.name}_fake_prop"),
        ],
    ):
        out = junit_parser.get_properties(testcase(name=tc_name, result=tc_result))
        assert out == expected_output


def test_get_properties_raises_exception(junit_parser):
    with pytest.raises(
        Exception, match=" does not have all required properties"
    ), patch.object(
        JunitParser,
        "yield_properties",
        lambda x, tc: [
            prop(name="data_model", value=f"data_model"),
            prop(name="data_set", value=f"data_set"),
            prop(name="fields", value=f"fields"),
            prop(name="tag_stanza", value=f"tag_stanza"),
            prop(name="fake_prop", value=f"fake_prop"),
        ],
    ):
        junit_parser.get_properties(
            testcase(name="test_cim_required_fields", result=None)
        )


def test_yield_properties(junit_parser):
    tc = MagicMock()
    tc.child.side_effect = lambda x: (
        item
        for item in [
            "data_model",
            "data_set",
            "fields",
            "tag_stanza",
            "fields_type",
            "fake_prop",
        ]
    )
    out = list(junit_parser.yield_properties(tc))
    assert out == [
        "data_model",
        "data_set",
        "fields",
        "tag_stanza",
        "fields_type",
        "fake_prop",
    ]


def test_generate_report(junit_parser, cim_report_generator_mock):
    junit_parser.data = ["test_data"]
    with patch.object(JunitParser, "parse_junit") as parse_junit_mock:
        junit_parser.generate_report("fake_path")
        parse_junit_mock.assert_called_once_with()
        cim_report_generator_mock.assert_has_calls(
            [call(["test_data"]), call.generate_report("fake_path")]
        )


def test_main(argparse_mock, junit_parser_mock):
    junit_parser_mock.data = True
    args = namedtuple("Namespace", ["junit_xml", "report_path"])
    argparse_mock.parse_args.return_value = args("junit_xml_path", "report_path")
    main()
    junit_parser_mock.assert_has_calls(
        [
            call("junit_xml_path"),
            call.parse_junit(),
            call.generate_report("report_path"),
        ]
    )


def test_main_without_junit_data(argparse_mock, junit_parser_mock, sys_exit_mock):
    junit_parser_mock.data = False
    main()
    sys_exit_mock.assert_called_once_with(
        "No CIM Compatibility tests found in JUnit XML"
    )
