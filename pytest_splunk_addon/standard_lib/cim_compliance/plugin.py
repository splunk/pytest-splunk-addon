"""
Plugin to generate the report dynamically after executing the test cases
"""
import pytest
import time
import os


class CIMReportPlugin(object):
    def __init__(self, config):
        self.config = config
        self.content = ""
        self.data = []
        has_rerun = config.pluginmanager.hasplugin("rerunfailures")
        self.rerun = 0 if has_rerun else None
        self.report_path = ""

    def _save_report(self, report):
        self.md_file.write(report)
        self.md_file.close()

    def _generate_report(self, session):
        return self.data

    def append_failed(self, report):
        pass

    def pytest_sessionstart(self, session):
        """
        Init the markdown file
        """
        self.md_file = open(os.path.join(self.report_path, "temp.md"), "a")
        self.suite_start_time = time.time()

    def pytest_sessionfinish(self, session):
        """
        Save the report.
        """
        report_content = self._generate_report(session)
        self._save_report(report_content)

    def pytest_collectreport(self, report):
        """
        To catch the exception in collection
        """
        if report.failed:
            self.append_failed(report)

    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_logreport(self, report):
        if report.when == "call":

            self.data.append(
                {
                    report.user_properties[1][0]: report.user_properties[1][1],
                    report.user_properties[2][0]: report.user_properties[2][1],
                    report.user_properties[3][0]: report.user_properties[3][1],
                    report.user_properties[4][0]: report.user_properties[4][1],
                    "status": report.outcome,
                }
            )

    def pytest_terminal_summary(self, terminalreporter):
        terminalreporter.write_sep("-", "generated markdown file.!")
