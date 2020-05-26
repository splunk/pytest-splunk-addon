"""
Parse the Junit XML report and convert it to required format
"""
from ca_report_generator import CIMReportGenerator
import argparse
import errno
import os
from junitparser import JUnitXml, Properties


class JunitParser(object):
    def __init__(self, junit_path, report_path):
        if os.path.isfile(junit_path):
            self._junitfile = junit_path
        elif os.path.isdir(junit_path):
            raise Exception(
                "Generating Report for multiple xml is not currently Supported."
            )
        else:
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), junit_path
            )
        self.report_path = report_path
        self._xml = JUnitXml.fromfile(self._junitfile)

    def parse_junit(self):
        xml = self._xml
        self.data = []

        for suites in xml:
            for tc in suites:
                if "test_cim_required_fields" in tc.name and (
                    not tc.result or tc.result._tag == "failure"
                ):
                    self.data.append(self.get_properties(tc))

    def get_properties(self, testcase):
        row_template = {
            "data_model": "-",
            "data_set": "-",
            "field": None,
            "status": "Fail" if testcase.result else "Pass",
            "tag_stanza": "-",
        }
        props = self.yield_properties(testcase)
        for prop in props:
            if prop.name in row_template:
                row_template[prop.name] = prop.value
        return row_template

    def yield_properties(self, testcase):
        props = testcase.child(Properties)
        if props is None:
            return
        for prop in props:
            yield prop

    def generate_report(self):
        report_gen = CIMReportGenerator(self.data)
        report_gen.generate_report(self.report_path)


def main():
    # Parse Args using arg parse
    # Parse Junit path : input
    # parse report path : output
    junitparserobj = JunitParser(
        "G:\\My Drive\\TA-Factory\\automation\\cim_report\\trial1.xml",
        "demo.md",
    )
    junitparserobj.parse_junit()
    junitparserobj.generate_report()


if __name__ == "__main__":
    main()
