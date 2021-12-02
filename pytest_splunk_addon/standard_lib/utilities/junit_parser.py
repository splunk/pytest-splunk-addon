#
# Copyright 2021 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Parse the Junit XML report and convert it to required format
"""
from ..cim_compliance import CIMReportGenerator
import argparse
import errno
import os
import sys
from html import escape, unescape
from junitparser import JUnitXml, Properties, Skipped, Failure, TestCase


class JunitParser(object):
    def __init__(self, junit_xml_path):
        if os.path.isfile(junit_xml_path):
            self._junitfile = junit_xml_path
        elif os.path.isdir(junit_xml_path):
            raise Exception(
                "Generating Report for multiple xml is not currently Supported."
            )
        else:
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), junit_xml_path
            )

        self._xml = JUnitXml.fromfile(self._junitfile)

    def parse_junit(self):
        """
        Function to parse the provided JUnit XML.
        It creates and adds a list of dictionaries `data` to object properties.
        """
        xml = self._xml
        self.data = []

        for suites in xml:
            for tc in suites:
                if "test_cim_required_fields" in tc.name:
                    try:
                        # This mimics the same behaviour we had when
                        # junitparser<2 had only 1 result per test case.
                        result = tc.result[0]
                        if isinstance(result, (Skipped, Failure)):
                            self.data.append(self.get_properties(tc))
                    except IndexError:
                        self.data.append(self.get_properties(tc))

    def get_properties(self, testcase: TestCase):
        """
        Function to get all the properties of a testcase.

        Args:
            testcase: Contains all the data of a Testcase.

        Returns:
            Dictionary: dictionary with all the required properties of Testcase.
        """
        try:
            result = testcase.result[0]
            status = "failed" if isinstance(result, Failure) else "skipped"
            test_property = (
                "-"
                if not status == "failed"
                else escape(unescape(result.message.splitlines()[0])[:100])
            )
        except IndexError:
            status = "passed"
            test_property = "-"
        row_template = {
            "status": status,
            "test_property": test_property,
        }
        for prop in self._yield_properties(testcase):
            if prop.name in [
                "data_model",
                "data_set",
                "fields",
                "tag_stanza",
                "fields_type",
            ]:
                row_template[prop.name] = prop.value

        if len(row_template) != 7:
            raise Exception(f"{testcase.name} does not have all required properties")
        return row_template

    def _yield_properties(self, testcase):
        """
        Function to yield properties of a Testcase

        Args:
            testcase(junitparser.TestCase): Contains all the data of a Testcase.

        Yields:
            junitparser.Property: Property object of a Testcase.
        """
        yield from testcase.child(Properties)

    def generate_report(self, report_path):
        self.parse_junit()
        report_gen = CIMReportGenerator(self.data)
        report_gen.generate_report(report_path)


def main():
    """
    Entrypoint to the script.
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("junit_xml", help="Path to JUnit XML file", metavar="junit-xml")
    ap.add_argument(
        "report_path",
        help="Path to Save Report",
        metavar="report-path",
        nargs="?",
        default="cim_report.md",
    )
    args = ap.parse_args()

    junit_xml_path = args.junit_xml
    report_path = args.report_path

    ju_p = JunitParser(junit_xml_path)
    ju_p.parse_junit()
    if ju_p.data:
        ju_p.generate_report(report_path)
    else:
        sys.exit("No CIM Compatibility tests found in JUnit XML")


if __name__ == "__main__":
    main()
