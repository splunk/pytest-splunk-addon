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
        # self.passed = []
        # self.failed = []
        # self.skipped = []
        self.data = []
        has_rerun = config.pluginmanager.hasplugin("rerunfailures")
        self.rerun = 0 if has_rerun else None

    def _save_report(self, report):
        self.md_file.write(report)
        self.md_file.close()

    def _generate_report(self, session):
        _template = "\n".join(
            [
                "# Report",
                "=" * 30,
                str([each.nodeid for each in self.passed]),
                str([each.nodeid for each in self.failed]),
                str([each.nodeid for each in self.skipped]),
            ]
        )
        return _template

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
            if report.passed:
                self.passed.append(report)
            elif report.failed:
                self.failed.append(report)
            elif report.skipped:
                self.skipped.append(report)

            # print("OUTCOME::" + str(report.outcome))
            # print("FAILED::" + str(report.failed))
            # print("PROPERTY::" + str(report.user_properties))
            # print("NODEID::" + str(report.nodeid))

    def pytest_terminal_summary(self, terminalreporter):
        terminalreporter.write_sep("-", "generated markdown file.!")
