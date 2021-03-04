import pytest
from unittest.mock import MagicMock, call
from collections import namedtuple
from pytest_splunk_addon.standard_lib.cim_compliance.plugin import CIMReportPlugin

config = namedtuple("Config", ["getoption"])
cim_config = config(getoption=lambda x: f"path_{x}")
report = namedtuple(
    "Report", ["when", "nodeid", "outcome", "user_properties", "longrepr"]
)
cim_report_passed = report(
    when="call",
    nodeid="test_cim_required_fields",
    outcome="passed",
    user_properties=[
        ("tag_stanza", "fake_tag_stanza"),
        ("data_model", "fake_data_model"),
        ("tag", "fake_tag"),
    ],
    longrepr=None,
)
longrepr = MagicMock()
longrepr.reprcrash.message = "test error message"
cim_report_failed = report(
    when="call",
    nodeid="test_cim_required_fields",
    outcome="failed",
    user_properties=[
        ("tag_stanza", "fake_tag_stanza"),
        ("data_model", "fake_data_model"),
        ("tag", "fake_tag"),
    ],
    longrepr=longrepr,
)
cim_report_failed_without_message = report(
    when="call",
    nodeid="test_cim_required_fields",
    outcome="failed",
    user_properties=[
        ("tag_stanza", "fake_tag_stanza"),
        ("data_model", "fake_data_model"),
        ("tag", "fake_tag"),
    ],
    longrepr=None,
)


@pytest.fixture()
def cim_report_plugin():
    return CIMReportPlugin(cim_config)


@pytest.fixture()
def cim_report_generator_mock(monkeypatch):
    crg = MagicMock()
    crg.return_value = crg
    monkeypatch.setattr(
        "pytest_splunk_addon.standard_lib.cim_compliance.plugin.CIMReportGenerator",
        crg,
    )
    return crg


def test_pytest_sessionfinish(cim_report_plugin, cim_report_generator_mock):
    cim_report_plugin.data = ["fake_data", "abstract_data"]
    cim_report_plugin.pytest_sessionfinish("session")
    cim_report_generator_mock.assert_has_calls(
        [call(["fake_data", "abstract_data"]), call.generate_report("path_cim_report")]
    )


@pytest.mark.parametrize(
    "cim_report, expected_output",
    [
        (
            cim_report_passed,
            [
                {
                    "status": "passed",
                    "tag_stanza": "fake_tag_stanza",
                    "data_model": "fake_data_model",
                    "test_property": "-",
                }
            ],
        ),
        (
            cim_report_failed,
            [
                {
                    "status": "failed",
                    "tag_stanza": "fake_tag_stanza",
                    "data_model": "fake_data_model",
                    "test_property": "test error message",
                }
            ],
        ),
        (
            cim_report_failed_without_message,
            [
                {
                    "status": "failed",
                    "tag_stanza": "fake_tag_stanza",
                    "data_model": "fake_data_model",
                    "test_property": "-",
                }
            ],
        ),
    ],
)
def test_pytest_runtest_logreport(cim_report_plugin, cim_report, expected_output):
    cim_report_plugin.pytest_runtest_logreport(cim_report)
    assert cim_report_plugin.data == expected_output


@pytest.mark.parametrize(
    "data, expected_call",
    [
        (
            False,
            [
                call.write_sep(
                    "-",
                    "Markdown Report not generated as no CIM Compatibility tests were executed.",
                )
            ],
        ),
        (True, [call.write_sep("-", "Generated markdown report: path_cim_report")]),
    ],
)
def test_pytest_terminal_summary(cim_report_plugin, data, expected_call):
    cim_report_plugin.data = data
    terminal = MagicMock()
    cim_report_plugin.pytest_terminal_summary(terminal)
    terminal.assert_has_calls(expected_call)
