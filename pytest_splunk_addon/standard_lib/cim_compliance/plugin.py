"""
Plugin to generate the report dynamically after executing the test cases
"""
import pytest
import time
import os
from .ca_report_generator import CIMReportGenerator


class CIMReportPlugin(object):
    def __init__(self, config):
        self.data = []
        self.report_path = config.getoption("cim_report")

    def pytest_sessionfinish(self, session):
        """
        Generate the report.
        """
        report_generator = CIMReportGenerator(self.data)
        report_generator.generate_report(self.report_path)

    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_logreport(self, report):
        """
        Collect the data to be added into the report.
        """
        if report.when == "call" and "test_cim_required_fields" in report.nodeid:
            self.data.append(
                {
                    report.user_properties[1][0]: report.user_properties[1][1],
                    report.user_properties[2][0]: report.user_properties[2][1],
                    report.user_properties[3][0]: report.user_properties[3][1],
                    report.user_properties[4][0]: report.user_properties[4][1],
                    report.user_properties[5][0]: report.user_properties[5][1],
                    "status": report.outcome,
                    "skip_type": "pytest.xfail" if report.keywords.get("xfail") else "",
                }
            )

    def pytest_terminal_summary(self, terminalreporter):
        terminalreporter.write_sep("-", "Generated markdown report!")
