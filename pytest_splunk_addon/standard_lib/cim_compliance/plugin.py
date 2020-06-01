"""
Plugin to generate the report dynamically after executing the test cases
"""
import pytest
import time
import os
from .cim_report_generator import CIMReportGenerator


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
            data_dict = {}
            data_dict["status"] = report.outcome
            keys = ["tag_stanza", "data_model", "data_set", "fields", "fields_type"]
            for each_property in report.user_properties:
                if each_property[0] in keys:
                    data_dict[each_property[0]] = each_property[1]
            data_dict["test_property"] = "-"
            try:
                if report.outcome == "failed":
                    data_dict[
                        "test_property"
                    ] = report.longrepr.reprcrash.message.splitlines()[0][:100]
            except AttributeError as e:
                pass

            self.data.append(data_dict)

    def pytest_terminal_summary(self, terminalreporter):
        if self.data:
            terminalreporter.write_sep(
                "-", "Generated markdown report: {}".format(self.report_path)
            )
        else:
            terminalreporter.write_sep(
                "-",
                "Markdown Report not generated as no CIM Compatibility tests were executed.",
            )
